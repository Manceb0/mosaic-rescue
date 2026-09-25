"""Render a MOSAIC RESCUE film page to MP4, frame by frame (deterministic).

Uso:
    python render_mp4.py <url_or_html_path> <salida.mp4> [fps]

Requiere: pip install playwright imageio-ffmpeg  (usa Microsoft Edge ya instalado; no descarga navegadores)
Cada fotograma se dibuja con window.MOSAIC_RESCUE.renderFrame(t); el audio se renderiza offline
(OfflineAudioContext) con el mismo guion de sonido y se une con ffmpeg.
"""
import base64
import pathlib
import subprocess
import sys
import time

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

AUDIO_JS = r"""
async () => {
  const M = window.MOSAIC_RESCUE;
  if (M.audioWavBase64) return await M.audioWavBase64();
  // v1: build the offline graph from the page's own audio functions
  const sr = 48000, off = new OfflineAudioContext(2, Math.ceil(sr * (M.duration + 0.5)), sr);
  const graph = makeGraph(off, off.destination), dry = off.createGain(), send = off.createGain();
  dry.connect(graph.master); send.connect(graph.conv);
  scheduleAll({ ac: off, dry, send, gate: graph.gate, nodes: [], noise: graph.noise, now: 0 }, 0, 0);
  const buf = await off.startRendering(), n = buf.length, L = buf.getChannelData(0), R = buf.getChannelData(1);
  const out = new Uint8Array(44 + n * 4), dv = new DataView(out.buffer);
  const ws = (o, s) => [...s].forEach((c, i) => dv.setUint8(o + i, c.charCodeAt(0)));
  ws(0, 'RIFF'); dv.setUint32(4, 36 + n * 4, true); ws(8, 'WAVE'); ws(12, 'fmt '); dv.setUint32(16, 16, true);
  dv.setUint16(20, 1, true); dv.setUint16(22, 2, true); dv.setUint32(24, sr, true); dv.setUint32(28, sr * 4, true);
  dv.setUint16(32, 4, true); dv.setUint16(34, 16, true); ws(36, 'data'); dv.setUint32(40, n * 4, true);
  for (let i = 0; i < n; i++) {
    dv.setInt16(44 + i * 4, Math.max(-1, Math.min(1, L[i])) * 32767, true);
    dv.setInt16(46 + i * 4, Math.max(-1, Math.min(1, R[i])) * 32767, true);
  }
  let s = ''; for (let i = 0; i < out.length; i += 0x8000) s += String.fromCharCode.apply(null, out.subarray(i, i + 0x8000));
  return btoa(s);
}
"""

FRAME_JS = """t => { MOSAIC_RESCUE.renderFrame(t);
  return document.getElementById('c').toDataURL('image/jpeg', 0.95).slice(23); }"""


def main():
    src, out = sys.argv[1], pathlib.Path(sys.argv[2])
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    url = src if src.startswith(('http:', 'https:', 'file:')) else pathlib.Path(src).resolve().as_uri()
    url += ('&' if '?' in url else '?') + 'export=1'
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    wav = out.with_suffix('.wav')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
        page.goto(url)
        page.wait_for_function("window.MOSAIC_RESCUE && document.fonts.status === 'loaded'", timeout=60000)
        time.sleep(1.0)
        page.evaluate("() => { MOSAIC_RESCUE.pause && MOSAIC_RESCUE.pause(); }")
        dur = page.evaluate('MOSAIC_RESCUE.duration')
        wav.write_bytes(base64.b64decode(page.evaluate(AUDIO_JS)))
        n = round(dur * fps)
        cmd = [ff, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg', '-i', '-',
               '-i', str(wav), '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', '-color_range', 'tv',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-tune', 'animation',
               '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        t0 = time.time()
        for f in range(n):
            proc.stdin.write(base64.b64decode(page.evaluate(FRAME_JS, f / fps)))
            if f % (fps * 5) == 0:
                print(f'{f}/{n} frames · {time.time() - t0:.0f}s', flush=True)
        proc.stdin.close()
        proc.wait()
        browser.close()
    wav.unlink(missing_ok=True)
    print('OK', out, f'{out.stat().st_size / 1e6:.1f} MB', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
