import { createApp } from 'vue'
import App from './app.vue'
import router from './router'
import "@/assets/tailwind.css"
import { LocalizationUtilities } from './utilities/localization-utilities'

import Components from "@/components";
import Modals from "@/modals";
import InventWidgets from "@/views/builder/components/page-editor/widgets";
import "@/data/providers/icon-provider";

addEventListener('mpy:done', () => {
    LocalizationUtilities.loadPreferredLanguageAsync().then(() => {
        createApp(App)
            .use(router)
            .use(Components)
            .use(Modals)
            .use(InventWidgets)
            .mount('#app');
    });
});