./animate.py ../../DLG-2021-06-20.csv "Alt(m)" 1201.4 130 --out-duration 114 --fps=50
ffmpeg -i ~/ar/MM/VIDEO/GH012220.MP4-00.03.38.077-00.05.30.815.MP4 -i movie.mov -filter_complex 'overlay=0:main_h-overlay_h+30:shortest=1' -c:v libx264 -c:a copy -preset slow -crf 18 flight-hq.mkv
