#ifndef CRYPTO_H
#define CRYPTO_H

#if defined(_WIN32) || defined(_WIN64)
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

extern "C" {
    DLL_EXPORT char* generateXVersion(const char* fileId, const char* expires);
    DLL_EXPORT void free_result(char* result);
}
#endif // CRYPTO_H
