<script lang="ts">
    import { DEFAULT_PITCH_SCALER, DEFAULT_TEMPO_SCALER, MAX_FILE_SIZE, ALLOWED_FORMATS } from '../globals';
    import { convert_audio } from '../api';
    import AudioPlayer from './AudioPlayer/AudioPlayer.svelte';

    let converting = false;
    let convert_status = '';
    let errorMessage: string | undefined = undefined;
    let desiredFormat = "ogg";
    let tempoScaler = DEFAULT_TEMPO_SCALER;
    let pitchScaler = DEFAULT_PITCH_SCALER;
    let file: FileList;

    let lastConverted: string | undefined = undefined;

    function convert() {
        if (!ALLOWED_FORMATS.includes(desiredFormat)) {
            errorMessage = `Format ${desiredFormat} not allowed`;
            return;
        } else if (!tempoScaler || tempoScaler > 10 || tempoScaler < 0) {
            errorMessage = "Tempo scale factor must be between 0 and 10 (inclusive)."
            return;
        } else if (!pitchScaler || pitchScaler > 10 || pitchScaler < 0) {
            errorMessage = "Pitch scale factor must be between 0 and 10 (inclusive)."
            return;
        } else if (!file || file.length === 0) {
            errorMessage = "Please select a file to convert."
            return;
        } else if (file[0].size > MAX_FILE_SIZE) {
            errorMessage = "File is too large."
            return;
        }
        on_status('Uploading');
        converting = true;
        errorMessage = undefined;

        convert_audio(file[0], desiredFormat, pitchScaler, tempoScaler, on_status).then(result => {
            lastConverted = result;
        }).catch(err => {
            errorMessage = err;
        }).finally(() => {
            converting = false;
            convert_status = '';
        });
    }

    function on_status(message: string) {
        convert_status = message;        
    }
</script>


    {#if errorMessage !== undefined}
        <div class="error">
            <p>{errorMessage}</p>
        </div>
    {/if}


    <form on:submit|preventDefault="{convert}">
        <input bind:files={file} type="file" name="file" accept="audio/ogg,audio/mpeg,audio/wav,audio/opus,audio/x-flac" disabled='{converting}'>
            
        <div class="grid">
            <label for="tempo-scaler">
                Scale Tempo
                <input bind:value={tempoScaler} type="number" name="tempo-scaler" step=0.05 min="0" max="10" disabled='{converting}'>
            </label>
            <label for="pitch-scaler">
                Scale Pitch
                <input bind:value={pitchScaler} type="number" name="pitch-scaler" step=0.05 min="0" max="10" disabled='{converting}'>
            </label>
            <label for="format">
                Output Format
                <select bind:value={desiredFormat} id="format" disabled='{converting}'>
                    {#each ALLOWED_FORMATS as format}
                        <option value={format}>
                            {format.toUpperCase()}
                        </option>
                    {/each}
                </select>
            </label>
        </div>

        <button type="submit" id="convert_button" disabled='{converting}' aria-busy='{converting}'>{converting ? convert_status : 'Convert'}</button>
    </form>

    
    {#if lastConverted}
        <h5 id="resultheader">Conversion Result</h5>
        <small>Converted files are only retained for 24 hours. Download files that you wish to keep.</small>
        <div class="player-wrapper">
            <AudioPlayer display={lastConverted}></AudioPlayer>
        </div>
    {/if}

<style>
#convert_button {
    max-width: 200px;
    min-width: 150px;
    margin-left: auto;
    margin-right: 0;
    margin-bottom: 10px;
}

.error {
    background-color: #d32f2f;
    border-radius: 0.25em;
    padding: 10px;
    margin-bottom: 20px;
}

p {
    margin: 0;
    color: white;
}

#resultheader {
    margin-top: 10px;
    margin-bottom: 0;
}

.player-wrapper {
    display: flex;
    justify-content: center;
    width: 100%
}
</style>