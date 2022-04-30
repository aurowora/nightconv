<script lang="ts">
import { get_recent_files } from "../api";
import AudioPlayer from "./AudioPlayer/AudioPlayer.svelte";

let fetchData = get_recent_files();

export function reload() {
    /* This causes Svelte to re-run the await block below */
    fetchData = get_recent_files();
}

</script>


<article>
    <header>
        <h4>Recent Conversions</h4>
    </header>
    <div class="players">
        {#await fetchData}
            <span aria-busy="true">Loading recently converted files...</span>
        {:then result}
            {#if result.length === 0}
                <span>No files have been converted within the past 24 hours.</span>
            {:else}
                {#each result as file}
                    <AudioPlayer display={file}></AudioPlayer>
                {/each}
            {/if}
        {:catch error}
            <img class="error-icon" alt="error icon" src="/assets/exclamation-triangle.svg" />
            <span class="error-text">An error occurred fetching the list of recently converted files.</span>
        {/await}
    </div>
</article>

<style>
    h4 {
        margin-bottom: 0;
    }

    .players {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: start;
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
</style>