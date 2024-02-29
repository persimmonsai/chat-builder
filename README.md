# Conversation Generation
The end goal is to generation training data in the form of conversations for a language model. For this, we will use `llama.cpp`.

## Setup
We'll first need to clone the repository, build the project, and download the model weights. We'll use a "small" model, Phi 2B. We can always use larger models (e.g. Lamma2 7B) if needed.

```console
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
```

Run `make` to build the project, or see below to add support for gpu acceleration.

### GPU Acceleration (optional)
Llama.cpp supports GPU Acceleration with CUBLAS. First ensure you have applicable hardware such as an NVIDIA graphics card. Then, install [`nvidia-cuda-toolkit`](https://developer.nvidia.com/cuda-downloads) on your system, ensuring `nvcc` runs.

Then, we can instead build with `make LLAMA_CUBLAS=1`. When starting the binary, we can also use the runtime argument `-ngl` to specify a number of gpu layers.

```
make LLAMA_CUBLAS=1
./main -m phi-2.Q4_K_M.gguf -i -ngl 20
```

## Testing
If everything ran properly, you should be able to chat and ask questions by running the following:

```console
MODEL=phi-2.Q4_K_M.gguf ./examples/chat-13B.sh
```

# Creating Conversations with the Chat Builder
We can use the `chat-builder` tool to generate conversations on keywords, directing the model with a configuration file. This `config.json` contains the words list, the input prompt, and other kinds of information on what the input response should and should not contain.

## Basic Setup
First, lets clone the repository and copy the script over.

```console
git clone https://github.com/persimmonsai/chat-builder.git
cp chat-builder/get-word-conversations.py /dir/to/llama.cpp/
```

Next, we need a base configuration file. Copy the following into `example.json` in your `llama.cpp` directory.

```json
{
	"name": "example",
	"model": "phi-2.Q4_K_M.gguf",
	"prompt_lines": [
		"We end this document with a conversation between a student and a teacher, where the teacher conveys the meaning of \"{word}\"",
		"STUDENT:"
	],
	"words" : [
		"bridge",
		"leaf",
		"pocket",
		"bear",
		"promises",
		"room",
		"village",
		"camera"
	],
	"exclude": [
		"relig",
		"sex",
		"gender",
		"politic",
		"kill"
	]
}
```

Now we can start generating conversations.

```console
python get-word-conversations.py example.json >> /tmp/example-conv.txt
```

If you built `llama.cpp` with `CUBLAS`, you can also pass in the `ngl` GPU layer argument directly into the `get-word-conversations.py` script.

```console
python get-word-conversations.py example.json -ngl 20 >> /tmp/example-conv.txt
```

## Conversations on a Specific Topic
Lets build a configuration file for a specific topic, in this case physics. We can create one from an online resource or generate one.

### Online Resource Generated Lists (recommended)
For this example, we will use Wikipedia's glossary of physics terms.

```console
wget -O - https://en.wikipedia.org/wiki/Glossary_of_physics  | grep '<dt class="glossary" .*<a .*>.*</a></dfn></dt>' | sed 's:.*><a .*>\(.*\)</a>.*:"\1",:g' > /tmp/physic-terms.txt
```

### Model Generated Lists
We can run something like the following to generate a list of physics related terms, but (in the writers experience at least) it generally has mixed results.

```console
./main -m phi-2.Q4_K_M.gguf -p 'The following is a list of 1000 physics terms. There will be NOTHING except physics terms next:\n"gravity", "force", "energy", "absolute zero", ' --escape
```

### Building the Configuration File
With our words list generated, we can transfer them into the `words` array in our new `physics.json` config file, derived from the example above. We can also make sure to adjust our prompt to say "...between a student and a **physics** teacher..."

From there, we can generate conversations like before.

```console
python get-word-conversations.py physics.json >> /tmp/physics-conv.txt
```

Experiment with your configuration file based on output, adjutsing the prompt, words, and excluded words as needed to ensure conversations remain on topic.

### Full Sending Generation
If all loks okay, we can use a simple bash script to generate conversations indefinitely. Note that conversations are written to the output file in "chunks", and you won't immediately see the written output until one iteration of the entire python script is completed.

Put the following into a `run.sh` script and run it to generate conversations.

```console
#!/bin/bash

if [ $# -ne 2 ]; then
    echo usage: run.sh config.json output.txt
    exit
fi

while true; do
	python get-word-conversations.py $1 >> $2
done
```

This takes arguments for the input configuration file and the output file, letting us generate conversations like this:

```console
./run.sh physics.json /tmp/physics-conv.txt
```
