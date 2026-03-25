/**
 * Generates solid-color PWA icons as valid PNG files using only Node built-ins.
 * Run: node generate-icons.mjs
 */
import { deflateSync } from 'zlib'
import { writeFileSync } from 'fs'

// Build CRC32 table
const crcTable = new Uint32Array(256)
for (let i = 0; i < 256; i++) {
  let c = i
  for (let k = 0; k < 8; k++) c = (c & 1) ? 0xedb88320 ^ (c >>> 1) : c >>> 1
  crcTable[i] = c
}
function crc32(buf) {
  let crc = 0xffffffff
  for (const byte of buf) crc = (crc >>> 8) ^ crcTable[(crc ^ byte) & 0xff]
  return (crc ^ 0xffffffff) >>> 0
}

function makeChunk(type, data) {
  const t = Buffer.from(type, 'ascii')
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length)
  const crcBuf = Buffer.alloc(4); crcBuf.writeUInt32BE(crc32(Buffer.concat([t, data])))
  return Buffer.concat([len, t, data, crcBuf])
}

function makePng(w, h, r, g, b) {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])

  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4)
  ihdr[8] = 8; ihdr[9] = 2 // 8-bit depth, RGB color

  // Build raw scanlines: filter-byte(0) + R,G,B per pixel
  const row = Buffer.alloc(1 + w * 3)
  for (let x = 0; x < w; x++) {
    row[1 + x * 3] = r; row[2 + x * 3] = g; row[3 + x * 3] = b
  }
  const raw = Buffer.concat(Array(h).fill(row))

  return Buffer.concat([
    sig,
    makeChunk('IHDR', ihdr),
    makeChunk('IDAT', deflateSync(raw)),
    makeChunk('IEND', Buffer.alloc(0)),
  ])
}

// Brand teal: #028090 = rgb(2, 128, 144)
const [r, g, b] = [2, 128, 144]

writeFileSync('public/pwa-192x192.png',     makePng(192, 192, r, g, b))
writeFileSync('public/pwa-512x512.png',     makePng(512, 512, r, g, b))
writeFileSync('public/apple-touch-icon.png', makePng(180, 180, r, g, b))

console.log('PWA icons generated: pwa-192x192.png, pwa-512x512.png, apple-touch-icon.png')
