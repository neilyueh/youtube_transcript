# conda update -n base -c defaults conda

import openai
import pydub
from pytube import YouTube
from moviepy.editor import *
from pydub import AudioSegment


# 請記得將你的 openai api key 放在 openai_key.txt 檔案中
# 檢查 pytube 的版本編號
# import pytube
# print(pytube.__version__)

# 下載 youtube 影音檔案 儲存為 mp4 格式
def download_youtube_video(url, output_path="downloads"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # you should be able to fix streamerror issue by
    # pip uninstall pytube
    # pip uninstall pytube3
    # python -m pip install git+https://github.com/nficano/pytube

    filename = ""
    try:
        yt = YouTube(url)
        # python -m pip install git+https://github.com/nficano/pytube
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        filename = video.default_filename
        video.download(output_path)
        print(f"Video downloaded and saved as: {os.path.join(output_path, filename)}")
    except Exception as e:
        print(f"Error: {e}")
        exit(-1)

    return os.path.join(output_path, filename)


# 將mp4 影音檔案中的聲音檔萃取出來 儲存為 wav & mp3 格式.
def extract_audio_from_video(video_path, output_path=None):
    output_path2 = ""
    #
    # pip install ffmpeg
    if not output_path:
        output_path = os.path.splitext(video_path)[0] + ".wav"
        output_path2 = os.path.splitext(video_path)[0] + ".mp3"

    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_path)

    # 將wav檔案載入成AudioSegment物件
    # conda install -c conda-forge ffmpeg
    sound = AudioSegment.from_wav(output_path)

    # 將AudioSegment物件輸出為mp3檔案
    print(output_path)
    print(output_path2)
    print(pydub.AudioSegment.converter)

    sound.export(output_path2, format="mp3")
    return output_path2


# 語音轉文字副程式
def transcribe_mp3_file(filex):
    # Transcribe audio to text using OpenAI API
    # 讀取音訊文件
    print(filex)
    with open(filex, "rb") as audio_file:
        model_id = 'whisper-1'
        response = openai.Audio.transcribe(
            model=model_id,
            file=audio_file)

    s_ret = str(response['text'].replace(' ', '\n'))
    print(s_ret)
    return s_ret


# 分割 mp3 檔案. 60秒一個檔案
def conv_mp3(mp3_file_p):
    # 設定分割後的檔案長度(毫秒), 30000 就是 30 秒一個檔案的意思.
    segment_length = 60000

    # 讀取要分割的檔案
    audio_file = AudioSegment.from_file(mp3_file_p, format="mp3")

    # 計算要分割的次數
    num_segments = len(audio_file) // segment_length + 1

    audio_files = []
    # 進行分割
    for i in range(num_segments):
        start = i * segment_length
        end = (i + 1) * segment_length
        segment = audio_file[start:end]
        segment.export(os.path.join(output_folder, f"output_{i}.mp3"), format="mp3")
        audio_files.append(os.path.join(output_folder, f"output_{i}.mp3"))
    #

    tran_script = ""
    for audio_file in audio_files:
        chunk_transcript1 = transcribe_mp3_file(audio_file)
        tran_script += chunk_transcript1

    return tran_script


def user_input(default_str):
    youtube_input = input("請輸入YouTube影片網址 :")
    if not youtube_input:
        youtube_input = default_str

    return youtube_input


def get_last_part_of_url(url):
    return url.split('/')[-1]


def read_openai_key():
    with open('openai_key.txt', 'r') as f_openai_key:
        api_key = f_openai_key.read().strip()
        # Set up OpenAI API key
        openai.api_key = api_key


if __name__ == "__main__":
    read_openai_key()
    youtube_url = user_input("https://youtu.be/2Xuei49DQ3w")
    print('要下載的影片是: %s' % youtube_url)

    # youtube_url = "https://youtu.be/2Xuei49DQ3w"
    # youtube_url = input("請輸入YouTube影片網址：")
    output_folder = "downloads"

    mp4_file_path = download_youtube_video(youtube_url, output_folder)
    print(f"影片已下載並儲存為：{mp4_file_path}")

    mp3_file_path = extract_audio_from_video(mp4_file_path)
    print(f"音頻已提取並儲存為：{mp3_file_path}")

    transcript = conv_mp3(mp3_file_path)

    transcript_file_path = os.path.join(output_folder, "transcript_" + get_last_part_of_url(youtube_url) + ".txt")
    with open(transcript_file_path, "w", encoding='UTF-8') as f:
        f.write(transcript)
        f.write("\n{0}".format(youtube_url))

    print(f"文字已經儲存為：{transcript_file_path}")
