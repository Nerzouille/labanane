<svelte:options runes={true} />
<script lang="ts">
  import { onMount } from 'svelte';

  let { blend = 0 }: { blend?: number } = $props();

  const VERT_SRC = `
    attribute vec2 a_position;
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

  const FRAG_SRC = `
    precision mediump float;
    uniform float u_time;
    uniform vec2  u_resolution;
    uniform float u_blend;

    float rand(vec2 co) {
      return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
    }

    void main() {
      vec2 uv = gl_FragCoord.xy / u_resolution;

      // Base: sombre → blanc
      vec3 color = mix(vec3(0.02, 0.02, 0.06), vec3(1.0, 1.0, 1.0), u_blend);

      // Glows s'estompent au fur et à mesure
      float glowFade = 1.0 - u_blend;

      vec2 d1 = uv - vec2(0.8, 0.2);
      color += vec3(0.35, 0.05, 0.7) * exp(-dot(d1,d1) * 2.5) * 1.3 * glowFade;

      vec2 d2 = uv - vec2(0.15, 0.85);
      color += vec3(0.05, 0.15, 0.7) * exp(-dot(d2,d2) * 2.0) * 0.9 * glowFade;

      // Vague : s'élargit et blanchit pour remplir l'écran
      float angle    = 2.618;
      vec2  dir      = vec2(cos(angle), sin(angle));
      vec2  perp     = vec2(-sin(angle), cos(angle));
      float proj     = dot(uv - vec2(0.5), dir);
      float perpProj = dot(uv - vec2(0.5), perp);
      float wave     = sin(proj * 8.0 - u_time * 0.6) * 0.04;
      float waveDist = perpProj - wave;

      // sharpness 7.0 → 0.0 : la vague s'élargit jusqu'à couvrir tout l'écran
      float sharpness = mix(7.0, 0.0, u_blend);
      float waveG     = mix(exp(-abs(waveDist) * sharpness), 1.0, u_blend);
      vec3  waveColor = mix(vec3(0.99, 0.59, 0.0) * 0.28, vec3(1.0), u_blend);
      color += waveColor * waveG;

      // Dither (s'estompe aussi)
      vec2  px    = floor(gl_FragCoord.xy / 1.5);
      float noise = rand(px) * 2.0 - 1.0;
      color += noise * 0.008 * glowFade;

      gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
    }
  `;

  let canvas: HTMLCanvasElement;

  onMount(() => {
    const gl = canvas.getContext('webgl');
    if (!gl) return;

    function compile(type: number, src: string): WebGLShader {
      const s = gl!.createShader(type)!;
      gl!.shaderSource(s, src);
      gl!.compileShader(s);
      if (!gl!.getShaderParameter(s, gl!.COMPILE_STATUS))
        console.error('Shader error:', gl!.getShaderInfoLog(s));
      return s;
    }

    const prog = gl.createProgram()!;
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT_SRC));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG_SRC));
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1,-1, 1,-1, -1,1,
      -1, 1, 1,-1,  1,1,
    ]), gl.STATIC_DRAW);

    const aPos = gl.getAttribLocation(prog, 'a_position');
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    const uTime  = gl.getUniformLocation(prog, 'u_time');
    const uRes   = gl.getUniformLocation(prog, 'u_resolution');
    const uBlend = gl.getUniformLocation(prog, 'u_blend');

    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      gl!.viewport(0, 0, canvas.width, canvas.height);
    }
    resize();
    window.addEventListener('resize', resize);

    const t0 = performance.now();
    let raf: number;
    function render() {
      gl!.uniform1f(uTime,  (performance.now() - t0) / 1000);
      gl!.uniform2f(uRes,   canvas.width, canvas.height);
      gl!.uniform1f(uBlend, blend);
      gl!.drawArrays(gl!.TRIANGLES, 0, 6);
      raf = requestAnimationFrame(render);
    }
    render();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  });
</script>

<canvas bind:this={canvas}></canvas>

<style>
  canvas {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
  }
</style>
