/**
 * Client-Side Encryption Library
 * Encrypts sensitive data using AES-256-GCM before sending to backend
 * Note: Backend also encrypts at rest, providing double encryption
 */

// For browser environments, use TweetNaCl.js or libsodium.js
// This is a simplified version using Web Crypto API (built-in)

async function deriveKey(password, salt = null) {
  const encoder = new TextEncoder()
  const passwordBuffer = encoder.encode(password)
  
  // Generate salt if not provided  
  if (!salt) {
    salt = crypto.getRandomValues(new Uint8Array(16))
  }

  // Use PBKDF2 to derive key
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveKey']
  )

  const key = await crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )

  return { key, salt }
}

export const encryption = {
  async encrypt(data, userSecret) {
    try {
      const { key } = await deriveKey(userSecret)
      const encodedData = new TextEncoder().encode(JSON.stringify(data))
      const iv = crypto.getRandomValues(new Uint8Array(12))

      const encryptedData = await crypto.subtle.encrypt(
        'AES-GCM',
        key,
        encodedData
      )

      // Combine IV + ciphertext and return base64
      const combined = new Uint8Array(iv.length + encryptedData.byteLength)
      combined.set(iv)
      combined.set(new Uint8Array(encryptedData), iv.length)

      return btoa(String.fromCharCode.apply(null, combined))
    } catch (error) {
      console.error('Encryption failed:', error)
      throw error
    }
  },

  async decrypt(encryptedData, userSecret) {
    try {
      const { key } = await deriveKey(userSecret)
      
      // Decode from base64
      const binaryData = atob(encryptedData)
      const combined = new Uint8Array(binaryData.length)
      for (let i = 0; i < binaryData.length; i++) {
        combined[i] = binaryData.charCodeAt(i)
      }

      // Extract IV and ciphertext
      const iv = combined.slice(0, 12)
      const ciphertext = combined.slice(12)

      // Decrypt
      const decryptedData = await crypto.subtle.decrypt(
        'AES-GCM',
        key,
        ciphertext
      )

      return JSON.parse(new TextDecoder().decode(decryptedData))
    } catch (error) {
      console.error('Decryption failed:', error)
      throw error
    }
  }
}
