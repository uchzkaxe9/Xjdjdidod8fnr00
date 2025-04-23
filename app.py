# Code by @AzRProjects_assistant_bot

from flask import Flask, request, send_file, jsonify, render_template_string, url_for
from pytube import YouTube
from moviepy.editor import AudioFileClip
import os
import uuid

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_get():
    url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')
    want_json = request.args.get('json', 'false').lower() == 'true'

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        yt = YouTube(url)
        title = yt.title
        file_id = str(uuid.uuid4())

        if format_type == 'mp3':
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_path = f'{file_id}.mp4'
            final_path = f'static/{file_id}.mp3'
            audio_stream.download(filename=audio_path)

            clip = AudioFileClip(audio_path)
            clip.write_audiofile(final_path)
            clip.close()
            os.remove(audio_path)

            file_size = os.path.getsize(final_path)
            download_url = url_for('static', filename=f'{file_id}.mp3', _external=True)

        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            final_path = f'static/{file_id}.mp4'
            video_stream.download(filename=final_path)
            file_size = os.path.getsize(final_path)
            download_url = url_for('static', filename=f'{file_id}.mp4', _external=True)

        if want_json:
            return jsonify({
                'title': title,
                'format': format_type,
                'download_url': download_url,
                'size_bytes': file_size
            })

        return render_template_string('''
            <h3>Downloaded: {{ title }}</h3>
            <a href="{{ download_url }}" download>Download {{ format }}</a>
        ''', title=title, format=format_type.upper(), download_url=download_url)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
