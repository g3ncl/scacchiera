---
title: "NFC Game Board - Software"
source: https://nfcgameboard.com/software/
author: Ben Bulsink
captured: 2026-07-24
tags:
  - clipping
---

# Software

One of the biggest challenges in the design of the described board was to achieve a response speed that matches the human manipulation and observation speed. So to have the system responding on tile movements within say half a second.

To achieve this, a completely different usage of the RFID tags is invented. Instead of accessing all of the tiles, the tags, on the board individually, one by one, a simultaneous reading of all tags on a row or a column is executed. A smart orthogonal coding of the tags allows identifying them all in the same reading operation.

[This method is described in this document BitwiseID](https://nfcgameboard.com/wp-content/uploads/2026/05/Bitwise-ID-version-2.1.pdf) — local copy: [files/Bitwise-ID-version-2.1.pdf](files/Bitwise-ID-version-2.1.pdf), transcribed at [[bitwiseid|the BitwiseID source summary]].

The result is an unrivalled fast response time of 0.35 seconds, as showed in the video. This response time is NOT slowing down even with 225 tiles on the board!

You should read and understand the BitwiseID method first, to understand the functions and data structures described on the page Embedded Software

- [Embedded software](/embedded) (not yet captured)
- [Windows presentation software](/presentation) (not yet captured)

---

Scrabble® is a registered trade mark of Hasbro and Mattel
Copyright © 2022-2026 Ben Bulsink | benbulsink@outlook.com | Powered by WordPress
