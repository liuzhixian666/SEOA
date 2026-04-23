const sharp = require('sharp')
const path = require('path')
const fs = require('fs')

const inputPng = path.join(__dirname, 'src/assets/ceea.png')
const outputIco = path.join(__dirname, 'build/evaluate.ico')

async function createBMPFromPNG(pngPath, size) {
  const rgbaBuffer = await sharp(pngPath)
    .resize(size, size, {
      kernel: 'lanczos3',
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .ensureAlpha()
    .raw()
    .toBuffer()
  
  const width = size
  const height = size
  const bpp = 32
  
  const rowSize = Math.ceil((width * (bpp / 8)) / 4) * 4
  const pixelDataSize = rowSize * height
  const headerSize = 40
  const dibSize = headerSize + pixelDataSize
  
  const dib = Buffer.alloc(dibSize)
  
  dib.writeUInt32LE(headerSize, 0)
  dib.writeInt32LE(width, 4)
  dib.writeInt32LE(height * 2, 8)
  dib.writeUInt16LE(1, 12)
  dib.writeUInt16LE(bpp, 14)
  dib.writeUInt32LE(0, 16)
  dib.writeUInt32LE(pixelDataSize, 20)
  dib.writeInt32LE(2835, 24)
  dib.writeInt32LE(2835, 28)
  dib.writeUInt32LE(0, 32)
  dib.writeUInt32LE(0, 36)
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const srcIdx = ((height - 1 - y) * width + x) * 4
      const dstIdx = headerSize + (y * rowSize) + (x * 4)
      
      if (srcIdx + 3 < rgbaBuffer.length && dstIdx + 3 < dib.length) {
        dib[dstIdx] = rgbaBuffer[srcIdx + 2]
        dib[dstIdx + 1] = rgbaBuffer[srcIdx + 1]
        dib[dstIdx + 2] = rgbaBuffer[srcIdx]
        dib[dstIdx + 3] = rgbaBuffer[srcIdx + 3]
      }
    }
  }
  
  return dib
}

async function createMaskFromPNG(pngPath, size) {
  const rgbaBuffer = await sharp(pngPath)
    .resize(size, size, {
      kernel: 'lanczos3',
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .ensureAlpha()
    .raw()
    .toBuffer()
  
  const maskRowSize = Math.ceil(size / 8)
  const maskDataSize = maskRowSize * size
  const mask = Buffer.alloc(maskDataSize, 0)
  
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const srcIdx = ((size - 1 - y) * size + x) * 4
      const alpha = rgbaBuffer[srcIdx + 3] || 0
      
      if (alpha < 128) {
        const byteIdx = Math.floor(x / 8) + y * maskRowSize
        const bitIdx = 7 - (x % 8)
        if (byteIdx < mask.length) {
          mask[byteIdx] |= (1 << bitIdx)
        }
      }
    }
  }
  
  return mask
}

async function generate() {
  try {
    const sizes = [16, 24, 32, 48, 64, 128, 256]
    const images = []
    
    for (const size of sizes) {
      const bmp = await createBMPFromPNG(inputPng, size)
      const mask = await createMaskFromPNG(inputPng, size)
      
      const imageData = Buffer.concat([bmp, mask])
      images.push({ size, data: imageData })
      console.log(`Created ${size}x${size} image`)
    }
    
    let totalImageSize = 0
    for (const img of images) {
      totalImageSize += img.data.length
    }
    
    const icoHeaderSize = 6
    const dirEntrySize = 16
    const icoSize = icoHeaderSize + (dirEntrySize * images.length) + totalImageSize
    const ico = Buffer.alloc(icoSize)
    
    ico.writeUInt16LE(0, 0)
    ico.writeUInt16LE(1, 2)
    ico.writeUInt16LE(images.length, 4)
    
    const dataStartOffset = icoHeaderSize + (dirEntrySize * images.length)
    
    let currentOffset = dataStartOffset
    
    for (let i = 0; i < images.length; i++) {
      const img = images[i]
      const entryOffset = icoHeaderSize + (i * dirEntrySize)
      
      ico.writeUInt8(img.size === 256 ? 0 : img.size, entryOffset)
      ico.writeUInt8(img.size === 256 ? 0 : img.size, entryOffset + 1)
      ico.writeUInt16LE(0, entryOffset + 2)
      ico.writeUInt16LE(1, entryOffset + 4)
      ico.writeUInt16LE(32, entryOffset + 6)
      ico.writeUInt32LE(img.data.length, entryOffset + 8)
      ico.writeUInt32LE(currentOffset, entryOffset + 12)
      
      img.data.copy(ico, currentOffset)
      currentOffset += img.data.length
    }
    
    fs.writeFileSync(outputIco, ico)
    console.log('ICO created:', outputIco)
    console.log('Size:', ico.length, 'bytes')
    console.log('Sizes included:', sizes.join(', '))
  } catch (err) {
    console.error(err)
  }
}

generate()
