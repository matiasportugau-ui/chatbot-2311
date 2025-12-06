module.exports = {
    apps: [
        {
            name: "bmc-chatbot",
            script: "unified_launcher.py",
            args: "--mode fullstack --production",
            interpreter: "python3",
            interpreter_args: "-u", // Unbuffered output
            cwd: "./",
            watch: false,
            ignore_watch: ["logs", "node_modules", ".next", "__pycache__", "*.log"],
            env: {
                NODE_ENV: "production",
            },
            restart_delay: 5000, // Wait 5 seconds before restarting
            max_restarts: 10,    // Stop restarting after 10 failures in a short time
            error_file: "./logs/pm2-error.log",
            out_file: "./logs/pm2-out.log",
            merge_logs: true,
            time: true           // Add timestamps to logs
        }
    ]
};
