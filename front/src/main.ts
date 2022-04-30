/*
Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation using version 3 of the License ONLY.

See LICENSE.txt for more information.

ncconv / nightconv - A webservice for converting audio files to nightcore.
*/

import './global.scss'

import App from './components/App.svelte';

const app = new App({
	target: document.body
});

export default app;
