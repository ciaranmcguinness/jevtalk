# JevTalk

Finally: A way to let Jev speak!

## What is Jev?

For those who haven't heard, Jev is a general purpose classifier model made by Typesafe AI, built on a LLM. Given a document and a set of questions, it can respond to those questions, giving the confidence and probability scores aswell.

## Why do this?

Funny.

## But actually, why? Aren't there other projects to let Jev talk?

Yes, but none of them were up to my standards. Due to Jev's architecture, they all either severly limit what Jev can say, picking from a list of predetermined words. Or, they generally lack coherency, due to just giving Jev a list of characters and running a spelling test. Additionally, the best one I've seen, lyramakesmusic's (jevbot)[https://github.com/lyramakesmusic/jevbot], has a really short context length and discards jev's messages.

## So, what did you do differently?

JevTalk comes from the pallet school of JLMs (Jev Language Models), but differs in one crucial way to most others. The pallet is not fixed, but instead written by GPT-6 Luna. Now, this might dilute Jev's personality a bit, but this is more than made up for in the massive improvement to clarity and comprehensability.

## Cool, how do I try it?

You can try it in two ways. The easiest is to just use (my hosted version)[https://jevtalk-sable.vercel.app/], but if you want to muck arround in the nuts and bolts (or I'm out of API credits for the day), you can also run it locally. To do that, clone the repo, enter credentials into ".env.example" and rename it to ".env", then run `uv run jevtalk`, and you're off to the races! You don't even need OpenAI and Typesafe credits for this, if you're in Hackclub and verified. Just get a key from (Hackclub AI)[https://ai.hackclub.com/keys], put it in for your OpenAI and Typesafe keys, and use the base URLs called out in the .env