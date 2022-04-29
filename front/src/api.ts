interface StatusCallback {
    (message: string): void;
}

interface CheckResponse {
    complete: boolean;
    position?: number;
    file_id?: string;
}

export async function convert_audio(file: File, format: string, scale_pitch: number, scale_tempo: number, status_cb: StatusCallback): Promise<string> {
    let b = new FormData();
    b.append('output_format', format);
    b.append('scale_pitch', scale_pitch.toString());
    b.append('scale_tempo', scale_tempo.toString());
    b.append('audio_file', file);

    let resp = await fetch('/api/convert/', {
        method: 'post',
        mode: 'cors',
        redirect: 'follow',
        body: b
    })

    let t = await resp.text();
    let j;

    try {
        j = JSON.parse(t);
    } catch (e) {
        throw `Unexpected Response: ${t}.`;
    }

    if (j.hasOwnProperty('task_id')) {
        return await wait_for_completion(j['task_id'], status_cb);
    } else if (j.hasOwnProperty('detail')) {
        throw j['detail'];
    } else {
        throw t;
    }
}

async function wait_for_completion(task_id: string, status_cb: StatusCallback): Promise<string> {
    while (true) {
        let resp = await fetch(`/api/convert/check?task_id=${task_id}`)
        let t = await resp.text();
        let j;

        try {
            j = JSON.parse(t);
        } catch (e) {
            throw `Unexpected Response: ${t}.`;
        }


        if (j.hasOwnProperty('complete')) {
            let obj = j as CheckResponse;

            if (obj.complete && obj.file_id) {
                return obj.file_id;
            } else if (obj.position && obj.position <= 1) {
                status_cb("Converting");
            } else {
                status_cb(`${obj.position - 1} Ahead`);
            }
        } else if (j.hasOwnProperty('detail')) {
            throw j['detail'];
        } else {
            throw t;
        }

        // This is sleep
        await new Promise(r => setTimeout(r, 1250));
    }
}

/*
    Get metadata regarding a file
*/

export interface AudioMetadata {
    filename: string;
    content_type: string;
    expire_time: string;
    length: number;
    file_id?: string;
}

export async function get_audio_info(file_id: string): Promise<AudioMetadata>
{
    let resp = await fetch(`/api/media/describe/${file_id}`)
    let t = await resp.text();

    try {
        return JSON.parse(t) as AudioMetadata;
    } catch (e) {
        throw `Unexpected Response: ${t}.`;
    }
}

export async function get_recent_files(): Promise<string[]> {
    let resp = await fetch('/api/media/recents');
    let t = await resp.text();

    try {
        return JSON.parse(t) as string[];
    } catch (e) {
        throw `Unexpected Response: ${t}`
    }
}