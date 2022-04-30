<script lang="ts">
	import Convert from './Convert.svelte';
	import Recents from './Recents.svelte';
	import Footer from './Footer.svelte';
	import { BUTTONS, MAX_FILE_SIZE } from '../globals';
	import filesize from 'filesize';

	let recents: Recents;
</script>

<main class="container">
	<div class="header-wrapper">
		<div class="inner-wrap">
			<img src="/assets/schleep.webp" class="eevee" alt="icon">
			<div class="headings">
				<h1>Nightconv</h1>
				<h3>Convert mp3, ogg, flac, and wav files up to {filesize(MAX_FILE_SIZE, {base: 2})} to nightcore.</h3>
			</div>
		</div>
		<div>
			{#each BUTTONS as icon}
				<a href="{icon.target}" target="_blank">
					<img src="{icon.src}" alt="{icon.alt}" class="{`icon ${icon.recolor ? "recolor" : ""}`}" />
				</a>
			{/each}
		</div>
	</div>
	<Convert on:conversion-finished={recents.reload}></Convert>
	<Recents bind:this={recents}></Recents>
</main>

<Footer></Footer>

<style>
	.header-wrapper {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.inner-wrap {
		display: flex;
	}

	.eevee {
		height: 90px;
		width: auto;
		margin-right: 10px;
	}

	@media screen and (max-width: 576px) {
		.eevee {
			display: none;
		}
	}

	img.icon {
		width: 2em;
		height: auto;
	}

	.recolor {
		filter: invert(100%) sepia(0%) saturate(7477%) hue-rotate(170deg) brightness(109%) contrast(108%);
	}
</style>