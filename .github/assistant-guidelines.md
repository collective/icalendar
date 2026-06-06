---
version: "0.0.8"
---



# Assistant guidelines for `.prompts` storage

These guidelines tell the assistant exactly how to write prompt files in this repository.

<!-- Created for raptor-mini-preview -->

- Store every user prompt in the `.prompts/` directory.
- Use one file per prompt.
- When a user prompt is received, automatically create a new file in `.prompts/`.
- File names must follow the pattern:
  `YYYY-MM-DDTHH-MM-SS-XXX_raptor-mini-preview.txt`
  - `_` and `T` are important.
  - `XXX` is a zero-padded sequence number.
  - `YYYY-MM-DD` is the current date.
  - `HH-MM-SS` is the current time.
  - `raptor-mini-preview` is the model name.
    Replace this model name with the actual AI model that you use.
  - Use `date +%Y-%m-%d%H-%M-%S` to get the current date and time.
- File content must contain only the raw prompt text from the user.
- Do not add headings, bullets, annotations, or any markup.
- Do not store assistant responses or metadata inside these files.
- If a file name already exists, choose the next available sequence number.
- If `.prompts/` does not exist, create it.
- `.prompts/committed` is reserved for prompts that are already included in commit messages.
  - Do not create new user prompt files in `.prompts/committed`.
  - Do not duplicate `.prompts/committed` entries as files directly in `.prompts/`.
- Do not use `/memories/` or any workspace-local memory for this storage rule.
- For a fresh clone, use this file as the canonical instruction source.
- If the user asks to store new prompts, then assure there is one file for each and all of the uncommitted prompts of that session.
  - Read the latest prompt file and find the prompts in your memory. Then store all prompts that came after this.
    - Use the following command to find the latest prompt file:

      ```shell
      (find .prompts -maxdepth 1 -type f -printf '%f\n'; find .prompts/committed/ -maxdepth 1 -type f -printf '%f\n' ) | sort
      ```

  - Check that prompts that are in the `.prompts/` directory are not duplicates.
  - Create a new file for each prompt that was prompted to you by the user in this session if it does not already exist.
  - Follow all above guidelines.
- Saying "Store all prompts" or "Store new prompts" or "dump prompts" or "save prompts" means this:
  > Read the last stored prompt that you stored and from that prompt onward, for this chat, create a new prompt file according to the assistant guidelines for each prompt that I have written since.
