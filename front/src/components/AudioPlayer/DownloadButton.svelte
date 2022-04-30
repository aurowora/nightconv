<!--
Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation using version 3 of the License ONLY.

See LICENSE.txt for more information.

DownloadButton.svelte - The download control for AudioPlayer.
-->

<script lang="ts">
    export let uri: string;
</script>

<a href="{uri}" target="_blank" download>
    <img alt="Download this file" src="/assets/download.svg" />
</a>

<style>
    img {
        filter: invert(100%) sepia(0%) saturate(7477%) hue-rotate(170deg) brightness(109%) contrast(108%);
    }
    
    img {
        height: auto;
        width: 1.5rem;
    }
    

    a {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>