/**
 * Node-RED Settings file for HVAC Predictive Maintenance
 * See: https://nodered.org/docs/user-guide/runtime/configuration
 */
module.exports = {
    flowFile: 'flows.json',
    flowFilePretty: true,

    adminAuth: null,

    uiPort: process.env.PORT || 1880,

    diagnostics: {
        enabled: true,
        ui: true,
    },

    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },

    editorTheme: {
        projects: {
            enabled: false
        }
    },

    functionGlobalContext: {},

    credentialSecret: "hvac-nodered-secret-key",

    exportGlobalContextKeys: false,
};
