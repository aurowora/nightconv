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