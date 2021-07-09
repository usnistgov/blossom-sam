#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define KEYFILE_LEN 16

int check_license_key(void) {
    FILE *fp;
    uint8_t key[KEYFILE_LEN];
    int i;
    uint32_t tmp = 0;

    fp = fopen("/etc/hellowashington/license.key", "rb");

    if(!fp) {
        return -1;
    }

    if(fread(key, 1, KEYFILE_LEN, fp) != KEYFILE_LEN) {
        return -2;
    }

    fclose(fp);

    for(i = 0; i < KEYFILE_LEN; ++i) {
        tmp += key[i];
    }

    if((tmp % 3) == 0 && (tmp % 7) == 0) {
        return 0;
    }

    return -3;
}

int main(int argc, char *argv[]) {
    printf("Hello, Washington starting up....\n");

    if(check_license_key()) {
        fprintf(stderr, "No valid license key found, exiting.\n");
        exit(EXIT_FAILURE);
    }

    printf("Verified license key as authentic.\n");
    printf("Welcome to the 'Hello, Washington' BloSS@M demo program.\n");
    return 0;
}
