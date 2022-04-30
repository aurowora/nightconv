<!--
Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation using version 3 of the License ONLY.

See LICENSE.txt for more information.

DurationSlider.svelte - The duration slider control for AudioPlayer.
-->

<script lang="ts">
    export let position: number;
    export let totalDuration: number;

    let slider: HTMLInputElement;

    import { createEventDispatcher } from "svelte";
    const ev = createEventDispatcher();

    function onSliderChanged() {
        ev('setPosition', {
            position: slider.valueAsNumber
        })
    }
</script>

<input bind:this="{slider}" type="range" name="duration-slider" class="duration-slider" min="0" max="{totalDuration}" on:input="{onSliderChanged}" on:change="{onSliderChanged}" value={position}>

<style lang="scss">
input[type="range"] {
		// Sorry chrome, I have better things to do
		&::-moz-range-progress {
			background-color: rgb(230, 26, 100); 
		}
		&::-ms-fill-lower {
			background-color: rgb(230, 26, 100); 
		}
	}
</style>