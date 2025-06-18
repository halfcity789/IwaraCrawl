#include <iostream>

#include <openssl/evp.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include "include/crypto.h"

static const char* SECRET = "5nFp9kmbNnHdAFhaqMvt";

DLL_EXPORT char* generateXVersion(const char* fileId, const char* expires) {
    if (expires == NULL || strlen(expires) == 0) {
        return NULL;
    }
    // 计算输入字符串长度
    size_t fileIdLen = strlen(fileId);
    size_t expiresLen = strlen(expires);
    size_t secretLen = strlen(SECRET);
    
    // 为拼接后的字符串分配空间 (fileId + "_" + expires + "_" + secret + '\0')
    size_t bufferSize = fileIdLen + expiresLen + secretLen + 3;
    char* buffer = (char*)malloc(bufferSize);
    if (!buffer) return NULL;
    
    // 拼接字符串: fileId_expires_secret
    snprintf(buffer, bufferSize, "%s_%s_%s", fileId, expires, SECRET);
    
    // 初始化 EVP 上下文
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (!ctx) {
        free(buffer);
        return NULL;
    }
    
    // 初始化 SHA1 摘要
    if (EVP_DigestInit_ex(ctx, EVP_sha1(), NULL) != 1) {
        free(buffer);
        EVP_MD_CTX_free(ctx);
        return NULL;
    }
    
    // 更新摘要数据
    if (EVP_DigestUpdate(ctx, buffer, strlen(buffer)) != 1) {
        free(buffer);
        EVP_MD_CTX_free(ctx);
        return NULL;
    }
    
    // 获取最终摘要
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len;
    if (EVP_DigestFinal_ex(ctx, digest, &digest_len) != 1) {
        free(buffer);
        EVP_MD_CTX_free(ctx);
        return NULL;
    }
    
    // 清理资源
    free(buffer);
    EVP_MD_CTX_free(ctx);
    
    // 将二进制哈希转换为十六进制字符串
    char* hex_result = (char*)malloc((digest_len * 2) + 1);
    if (!hex_result) return NULL;
    
    for (unsigned int i = 0; i < digest_len; i++) {
        sprintf(hex_result + (i * 2), "%02x", digest[i]);
    }
    hex_result[digest_len * 2] = '\0';
    
    return hex_result;
}

// 清理函数
DLL_EXPORT void free_result(char* result) {
    if (result) {
        free(result);
    }
}