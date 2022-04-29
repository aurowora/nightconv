<script lang="ts">
    import { get_audio_info } from "../api"
    import PlayButton from './PlayButton.svelte';
    import DownloadButton from './DownloadButton.svelte';
    import DurationSlider from './DurationSlider.svelte';
    import Duration from 'dayjs/plugin/duration';
    import dayjs from 'dayjs';
    import filesize from 'filesize';
    dayjs.extend(Duration);

    export let display: string;
    let trackLength: number = null;
    let currentPosition: number = 0;
    let audioPlayer: HTMLAudioElement;

    async function handlePlayButton(ev: CustomEvent<{ playing: boolean }>) {
        if (ev.detail.playing) {
            await audioPlayer.play()
        } else {
            audioPlayer.pause();
        }
    }

    function handleDurationUpdate() {
        const d = audioPlayer.duration;

        if (d === NaN || d === Infinity) {
            trackLength = null;
        } else {
            trackLength = d;
        }
    }

    function handlePlaybackUpdate() {
        currentPosition = audioPlayer.currentTime;
    }

    function reset() {
        currentPosition = 0;
        audioPlayer.fastSeek(0);
    }

    function seekTo(ev: CustomEvent<{position: number}>) {
        audioPlayer.currentTime = ev.detail.position;
    }
</script>


{#await get_audio_info(display)}
<article class="player-placeholder">
    <span aria-busy="true">Loading audio metadata...</span>
</article>
{:then result}
<article class="player">
    <div class="flex-wrapper">
        <div class="button-wrapper">
            <PlayButton on:set_audio_state="{handlePlayButton}"></PlayButton>
        </div>
        <div class="flex-main">
            <span class="filename">{result.filename}</span>
            <small>{dayjs.duration(currentPosition, 'seconds').format(currentPosition < 3600 ? 'm:ss' : 'H:mm::ss')} {trackLength ? `/ ${dayjs.duration(trackLength, 'seconds').format(trackLength < 3600 ? 'm:ss' : 'H:mm::ss')}` : ''} - {filesize(result.length, {base: 2})}</small>
        </div>
        <div class="button-wrapper">
            <DownloadButton uri="{encodeURI(`/api/media/file/${display}/${result.filename}`)}"></DownloadButton>
        </div>
    </div>
    <DurationSlider on:setPosition={seekTo} position="{currentPosition}" totalDuration="{trackLength}" />
    <audio on:durationchange="{handleDurationUpdate}" on:timeupdate="{handlePlaybackUpdate}" on:ended="{reset}" bind:this={audioPlayer}>
        <source src="{encodeURI(`/api/media/file/${display}/${result.filename}`)}" type="{result.content_type}">
    </audio>
</article>
{:catch error}
<article class="player-placeholder">
    <img class="error-icon" alt="error icon" src="/assets/exclamation-triangle.svg" />
    <span class="error-text">An error occurred while loading this file.</span>
</article>
{/await}


<style>

    .player {
        display: flex;
        flex-direction: column;
        justify-content: space-between; 
        padding-bottom: 0;
    }

    .player-placeholder {
       display: flex;
       justify-content: center;
       align-items: center; 
    }

    .error-icon {
        width: 2.5em;
        height: auto;
        filter: invert(22%) sepia(33%) saturate(5749%) hue-rotate(345deg) brightness(101%) contrast(89%);
        margin-right: 10px;
    }

    .error-text {
        color: #d32f2f;
    }

    .filename {
        overflow: hidden;
        max-height: 32px;
    }

    .button-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 8%;
    }

    article {
        padding-top: 1em;
        min-height: 10em;
        width: 100%; 
        margin: 10px 0;
    }
    
    /*
    @media screen and (min-width: 992px) {
        article {
            width: 50%;
        }
    }
    */

    /*
    @media screen and (max-width: 991px) {
        article {
            width: 100%;
        }
    }
    */

    div.flex-main {
        flex-grow: 3;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 75%;
    }

    div.flex-wrapper {
        display: flex;
        flex-grow: 1;
        gap: 7px;
    }

    small {
        opacity: 0.8;
        font-size: 0.75em;
    }
</style>