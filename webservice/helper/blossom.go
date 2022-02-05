package main

import (
    "os"
    "fmt"
    "io/ioutil"
    "encoding/json"
    "bufio"
    "io"

    "github.com/hyperledger/fabric-sdk-go/pkg/gateway"
    "github.com/hyperledger/fabric-sdk-go/pkg/core/config"
    "github.com/hyperledger/fabric-sdk-go/pkg/common/logging"
)

type Identity struct {
    Cert string
    Key string
    Msp string
}

type Tx struct {
    Identity Identity
    Profile string
    Channel string
    Contract string
    Endorser string
    Function string
    Args []string
    Transient map[string]string
}

func fillWallet(wallet *gateway.Wallet, txin Tx) error {
    cert, err := ioutil.ReadFile(txin.Identity.Cert)
    if err != nil {
        return err
    }

    key, err := ioutil.ReadFile(txin.Identity.Key)
    if err != nil {
        return err
    }

    id := gateway.NewX509Identity(txin.Identity.Msp, string(cert), string(key))
    return wallet.Put("user", id)
}

func ReadInputTx() (Tx, error) {
    var out Tx
    var err error

    st, err := os.Stdin.Stat()
    if err != nil {
        fmt.Fprintf(os.Stderr, "%v\n", err)
        os.Exit(1)
    }

    if st.Mode() & os.ModeNamedPipe == 0 {
        fmt.Fprintf(os.Stderr, "Pipe in input tx!\n")
        os.Exit(1)
    }


    r := bufio.NewReader(os.Stdin)
    buf := make([]byte, 0, 4096)

    for {
        input, err := r.ReadByte()
        if err != nil && err == io.EOF {
            break
        }
        buf = append(buf, input)
    }

    err = json.Unmarshal(buf, &out)
    return out, err
}

func main() {
    var err error

    // disable the logger so we don't get messages from the fabric sdk...
    logging.SetLevel("", logging.ERROR)

    // the webservice will pipe us in a transaction (see exampletx.json) on
    // stdin
    txin, err := ReadInputTx()
    if err != nil {
        fmt.Fprintf(os.Stderr, "Couldn't read input transaction: %v\n", err)
        os.Exit(1)
    }

    // build the wallet with the info from the transaction
    wallet := gateway.NewInMemoryWallet()
    if err = fillWallet(wallet, txin); err != nil {
        fmt.Fprintf(os.Stderr, "%v\n", err)
        os.Exit(1)
    }

    // connect to the blockchain, get to the right channel and find our smart
    // contract
    pf := txin.Profile
    gw, err := gateway.Connect(gateway.WithConfig(config.FromFile(pf)),
                               gateway.WithIdentity(wallet, "user"))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Failed to connect to fabric gateway: %v!\n",
                    err)
        os.Exit(1)
    }
    defer gw.Close()

    nw, err := gw.GetNetwork(txin.Channel)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Couldn't get channel: %v\n", err)
        os.Exit(1)
    }

    contract := nw.GetContract(txin.Contract)

    // Build the transaction
    var tx *gateway.Transaction
    endo := txin.Endorser

    if len(txin.Transient) == 0 {
        tx, err = contract.CreateTransaction(txin.Function,
                                             gateway.WithEndorsingPeers(endo))
    } else {
        newmap := make(map[string][]byte)
        for k, v := range txin.Transient {
            newmap[k] = []byte(v)
        }

        tx, err = contract.CreateTransaction(txin.Function,
                                             gateway.WithEndorsingPeers(endo),
                                             gateway.WithTransient(newmap))
    }

    if err != nil {
        fmt.Fprintf(os.Stderr, "Could not create transaction: %v\n", err)
        os.Exit(1)
    }

    // Go!
    result, err := tx.Submit(txin.Args...)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error running transaction: %v\n", err)
        os.Exit(1)
    }

    // Give the service back the result from the transaction and return a
    // success error code.
    fmt.Print("%v\n", result)
    os.Exit(0)
}
