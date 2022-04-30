<script lang="ts">
	import Convert from './Convert.svelte';
	import Recents from './Recents.svelte';
	import Footer from './Footer.svelte';
	import { MAX_FILE_SIZE } from '../globals';
	import filesize from 'filesize';
</script>

<main class="container">
	<div class="headings">
		<h1>Nightconv</h1>
		<h3>Convert mp3, ogg, flac, and wav files up to {filesize(MAX_FILE_SIZE, {base: 2})} to nightcore.</h3>
	</div>
	<Convert></Convert>
	<Recents></Recents>
</main>

<Footer></Footer>