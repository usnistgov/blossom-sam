#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define KEYFILE_LEN 16

int check_license_key(const uint8_t key[KEYFILE_LEN]) {
    int i;
    uint32_t tmp = 0;

    for(i = 0; i < KEYFILE_LEN; ++i) {
        tmp += key[i];
    }

    if((tmp % 3) == 0 && (tmp % 7) == 0) {
        return 0;
    }

    return -3;
}

int main(int argc, char *argv[]) {
    uint8_t key[KEYFILE_LEN] = { 0 };
    int i;
    FILE *fp;

    if(argc != 2) {
        exit(EXIT_FAILURE);
    }

    printf("Generating keyfile\n");
    srand(time(NULL));

    do {
        printf("Working....\n");

        for(i = 0; i < KEYFILE_LEN; ++i) {
            key[i] = (uint8_t)rand();
            printf("%d ", key[i]);
        }
        printf("\n");
    } while(check_license_key(key));

    fp = fopen(argv[1], "wb");
    if(!fp) {
        exit(EXIT_FAILURE);
    }

    fwrite(key, 1, KEYFILE_LEN, fp);
    fclose(fp);

    printf("Key written to %s\n", argv[1]);

    return 0;
}
