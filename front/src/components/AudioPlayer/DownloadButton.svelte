<script lang="ts">
    export let uri: string;
</script>

<a href="{uri}" target="_blank" download>
    <img alt="Download this file" src="/assets/download.svg" />
</a>

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
        width: 1.5rem;
    }
    

    a {
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>