import urllib.request
import json
import io

def upload_file(url, project_id, filename, content):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = io.BytesIO()
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="project_id"\r\n\r\n{project_id}\r\n'.encode())
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'.encode())
    body.write(b'Content-Type: video/mp4\r\n\r\n')
    body.write(content)
    body.write(f'\r\n--{boundary}--\r\n'.encode())

    req = urllib.request.Request(url, data=body.getvalue(), headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    })
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def api_post(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def api_get(url):
    res = urllib.request.urlopen(url)
    return json.loads(res.read().decode())

def run_test():
    print('--- STEP 1: CREATE PROJECT ---')
    proj = api_post('http://127.0.0.1:8420/api/projects', {
        'name': 'Projeto E2E Test',
        'description': 'Teste completo do funil',
        'path': 'default_workspace'
    })
    pid = proj['id']
    print('Created Project ID:', pid)

    print('\n--- STEP 2: UPLOAD VIDEO ---')
    uploaded_videos = upload_file('http://127.0.0.1:8420/api/videos/upload', pid, 'test_video_e2e.mp4', b'0'*1000)
    print('Uploaded Videos:', uploaded_videos)
    vid_id = uploaded_videos[0]['id']

    print('\n--- STEP 3: LIST PROJECT VIDEOS ---')
    videos_list = api_get(f'http://127.0.0.1:8420/api/videos/project/{pid}?skip=0&limit=500')
    print('Project Videos count:', len(videos_list['videos']))
    assert len(videos_list['videos']) > 0, 'No videos found!'

    print('\n--- STEP 4: CREATE SUBTITLE PRESET ---')
    preset = api_post('http://127.0.0.1:8420/api/subtitle-presets', {
        'name': 'Preset Viral Yellow',
        'font_family': 'Montserrat',
        'font_size': 48,
        'primary_color': '#FFFFFF',
        'outline_color': '#000000',
        'uppercase': True
    })
    print('Subtitle Preset ID:', preset['id'])

    print('\n--- STEP 5: CREATE EXPORT PROFILE ---')
    profile = api_post('http://127.0.0.1:8420/api/export-profiles', {
        'name': 'Instagram Reels 1080p',
        'resolution': '1080x1920',
        'fps': 30,
        'codec': 'h264',
        'bitrate': '8M'
    })
    print('Export Profile ID:', profile['id'])

    print('\n--- STEP 6: CREATE VIDEO TEMPLATE ---')
    tpl = api_post('http://127.0.0.1:8420/api/video-templates', {
        'name': 'Template Reels Completo',
        'description': 'Template para Reels com crop, zoom e legenda',
        'category': 'reels',
        'pipeline_config': [
            {'type': 'import'},
            {'type': 'crop', 'aspect_ratio': '9:16'},
            {'type': 'zoom', 'zoom_factor': 1.1},
            {'type': 'subtitle', 'preset_id': preset['id']}
        ]
    })
    print('Video Template ID:', tpl['id'])

    print('\n--- STEP 7: ENQUEUE JOB ---')
    job = api_post('http://127.0.0.1:8420/api/jobs/enqueue', {
        'video_id': vid_id,
        'template_id': tpl['id'],
        'export_profile_id': profile['id']
    })
    print('Enqueued Job ID:', job['id'], 'Status:', job['status'])

    print('\n--- STEP 8: CHECK JOBS LIST ---')
    jobs = api_get(f'http://127.0.0.1:8420/api/jobs/project/{pid}')
    print('Project Jobs count:', len(jobs))

    print('\n>>> FULL WORKFLOW SUCCESSFUL! ZERO ERRORS! <<<')

if __name__ == '__main__':
    run_test()
