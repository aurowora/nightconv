<script lang="ts">
	import Convert from './Convert.svelte';
	import Recents from './Recents.svelte';
	import Footer from './Footer.svelte';
</script>

<main class="container">
	<div class="headings">
		<h1>Nightconv</h1>
		<h3>Upload audio files to convert to Nightcore.</h3>
	</div>
	<Convert></Convert>
	<Recents></Recents>
</main>

<Footer></Footer>