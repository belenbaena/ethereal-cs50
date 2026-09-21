# ETHEREAL Universe 🫧

#### Video Demo: TODO

#### Description

ETHEREAL Universe is a web-based application built as my CS50 final project. It extends the existing ETHEREAL brand with a small account system while leaving the published public website unchanged.

Users can create an ETHEREAL account, sign in, remain authenticated through Flask sessions, choose their favorite ETHEREAL knowledge worlds, save them to a personal collection called **My Bubbles**, remove them later, and log out.

The application uses **Python and Flask** for backend routes, authentication, sessions, and application logic; **SQLite/SQL** for persistent relational data; **HTML and CSS** for the interface; and **JavaScript** for asynchronous save/remove interactions without reloading the page. Passwords are never stored directly. Werkzeug securely hashes passwords before they are written to the database.

The project intentionally has a focused scope. ETHEREAL's existing public website remains the visual and editorial entrance to the brand. This repository contains the separate interactive application layer that will eventually be linked from the public site's **Explore the Universe** button.

A more detailed README describing every project file, design choice, and final deployment will be completed before CS50 submission.
