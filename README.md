# si-watch

Checks a list of .si domain names every 3 minutes with the register.si website lookup.

- The list is in the repository variable `SI_DOMAINS` (space-separated). It is not in the code.
- When a name is free, the job fails and shows the name in an error annotation. GitHub then sends a failed-workflow email.
- Lookup errors give a warning only. They do not fail the job.

To change the list: Settings > Secrets and variables > Actions > Variables > `SI_DOMAINS`.
To stop: Actions > si-watch > Disable workflow.
