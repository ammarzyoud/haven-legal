# Haven — Legal Pages

Published policy pages for [Haven](https://github.com/ammarzyoud), a luxury
residential real estate platform in Amman, Jordan.

Served via GitHub Pages:

- `privacy.html` — Privacy Policy
- `terms.html` — Terms of Service
- `index.html` — index linking to both

## Editing

`src/*.txt` are the source of truth. Edit the text, rebuild, commit:

```bash
python3 build.py
```

`build.py` converts the plain text into the styled pages, applying Haven's
palette and typography. It also strips the internal "READ BEFORE PUBLISHING"
note from the public output, so that note can stay in the source files.

Any remaining `[PLACEHOLDER]` is rendered in bold on the page, so gaps are
obvious rather than easy to miss. The build prints how many are left.

## Status

> These documents are **drafts**. They were written to match how the platform
> actually handles data, but they have not been reviewed by a lawyer, and the
> bracketed placeholders — company name, registration number, registered
> address, contact details, retention periods, liability cap — are not yet
> filled in.
>
> Jordan's Personal Data Protection Law No. 24 of 2023 applies to Haven.
> Complete the placeholders and obtain legal review before collecting data
> from real clients.
