<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const ev = createEventDispatcher();

    enum ButtonStates {
        PLAYING,
        PAUSED
    }

    export let state = ButtonStates.PAUSED;

    function toggle_state() {
        state = (state == ButtonStates.PAUSED ? ButtonStates.PLAYING : ButtonStates.PAUSED);

        ev('set_audio_state', {
            playing: state == ButtonStates.PLAYING
        })
    }
</script>

<span on:click="{toggle_state}">
    {#if state == ButtonStates.PLAYING}
        <img src="/assets/pause.svg" alt="Pause" />
    {:else}
        <img src="/assets/play.svg" alt="Play" />
    {/if}
</span>

<style>
    @media (prefers-color-scheme: dark) {
        img {
            filter: invert(100%) sepia(0%) saturate(7477%) hue-rotate(170deg) brightness(109%) contrast(108%);
        }
    }

    @media (prefers-color-scheme: light) {
        img {
            filter: invert(24%) sepia(0%) saturate(1%) hue-rotate(5deg) brightness(102%) contrast(97%);
        }
    }

    img {
        height: auto;
        width: 2.5rem;
    }

    span {
        cursor: pointer;
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>