# mix-duo.sh <out.mp3>: the two singers, the lead a little left and the second a little right
# (its breath above 5 kHz cut 6 dB, a 3:1 compressor so its high notes don't dip, gain SECOND), a short hall send (WET), the record's
# instrumental BAND_DB (default 10) dB under the voices.
set -e
OUT=${1:-mix-duo.mp3}; WET=${WET:-0.025}; SECOND=${SECOND:-1.86}
VOX="[0:a]pan=stereo|c0=0.55*c0|c1=0.45*c0[l];[1:a]highshelf=f=5000:g=-6,acompressor=threshold=0.08:ratio=3:attack=15:release=200:makeup=2,pan=stereo|c0=0.45*c0|c1=0.55*c0,volume=$SECOND[s];[l]asplit[ld][ls];[s]asplit[sd][ss];[ls][3:a]afir=dry=1:wet=1:gtype=none[lw];[ss][3:a]afir=dry=1:wet=1:gtype=none[sw];[ld][sd][lw][sw]amix=inputs=4:normalize=0:weights=1 1 $WET $(python3 -c "print($WET/2)")[voxr]"
V=$(ffmpeg -hide_banner -i lead.wav -i second.wav -i backing_orig.wav -i hall.wav -filter_complex "$VOX;[voxr]volumedetect" -f null - 2>&1 | grep -o "mean_volume: [-0-9.]*" | grep -o "[-0-9.]*$")
B=$(ffmpeg -hide_banner -t 34 -i backing_orig.wav -af volumedetect -f null - 2>&1 | grep -o "mean_volume: [-0-9.]*" | grep -o "[-0-9.]*$")
G=$(python3 -c "print(round(10**(($V-${BAND_DB:-10}-($B))/20),3))")
nice -n 19 ffmpeg -loglevel error -threads 1 -y -i lead.wav -i second.wav -i backing_orig.wav -i hall.wav -filter_complex "$VOX;[2:a]volume=$G[bg];[voxr][bg]amix=inputs=2:normalize=0:duration=longest,volume=0.85,alimiter=limit=0.95[m]" -map "[m]" -codec:a libmp3lame -q:a 2 $OUT
echo "$OUT: voices $V dB, band gain $G"
