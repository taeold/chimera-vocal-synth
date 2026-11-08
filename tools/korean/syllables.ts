import { readFileSync } from "node:fs";
import { gunzipSync } from "node:zlib";
import { initChimera } from "/tmp/chimera-vocal-synth/src/wasm/chimera.ts";
await initChimera(readFileSync("/tmp/chimera-vocal-synth/src/wasm/chimera.wasm"));
const { EnglishG2P, lyricsToSyllables } = await import("/tmp/chimera-vocal-synth/src/wasm/engine.ts");
new EnglishG2P().setDictionaryText(gunzipSync(readFileSync("/tmp/chimera-vocal-synth/public/data/cmudict.txt.gz")).toString());
const ipa = (xs: { ipa: string }[]) => xs.map((x) => x.ipa).join("");
console.log(lyricsToSyllables(process.argv[2]).map((s: any) => `${s.text}[${ipa(s.onset)}${s.nucleus.ipa}${ipa(s.coda)}]`).join(" "));
