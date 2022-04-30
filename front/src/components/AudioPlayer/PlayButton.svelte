<!--
Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation using version 3 of the License ONLY.

See LICENSE.txt for more information.

PlayButton.svelte - Play/pause control for AudioPlayer.
-->

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
    img {
        filter: invert(100%) sepia(0%) saturate(7477%) hue-rotate(170deg) brightness(109%) contrast(108%);
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