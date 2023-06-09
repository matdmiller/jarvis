# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_basic_chat_gradio.ipynb.

# %% auto 0
__all__ = ['gradio_chat_history_to_openai_chat_completions_format', 'process_user_message', 'process_bot_message',
           'create_basic_ui', 'create_and_run_basic_ui']

# %% ../nbs/02_basic_chat_gradio.ipynb 4
import jarvis.secrets

# %% ../nbs/02_basic_chat_gradio.ipynb 5
import openai
import numpy as np
import os
import json
import gradio as gr
import datetime

# %% ../nbs/02_basic_chat_gradio.ipynb 23
def gradio_chat_history_to_openai_chat_completions_format(
    history:list[list[dict]] #Gradio chat history.
)->list[dict]:
    """Converts gradio chat history to OpenAI messages completions format."""
    chat_formatted_list = []
    for message_pair in history:
        chat_formatted_list.append({'role':'user', 'content': message_pair[0]})
        if message_pair[1] is not None:
            chat_formatted_list.append({'role':'assistant', 'content': message_pair[1]})
    return chat_formatted_list

# %% ../nbs/02_basic_chat_gradio.ipynb 24
def process_user_message(
    user_message:str, #Most recent message from user.
    history:list[list[str]] #Message history from gradio.Chatbot instance.
)->tuple[str,list[list[str]]]:
    """Add user message to 'history' and clear message textbox."""
    print('process_user_message',user_message,history)
    # if history is None: history = []
    return "", history + [[user_message, None]]

# %% ../nbs/02_basic_chat_gradio.ipynb 25
def process_bot_message(
    history:list[list[str]], #Message history from gradio.Chatbot instance.
    system_msg:str, #Most recent message from user.
    selected_model:str, #Selected OpenAI model for chat completion.
    temperature:float=0., #How deterministic the model results are.  See OpenAI docs.
    stream:bool=True, #Whether or not to stream the results or return all at once when the model has finished its response.
)->list[list[str]]:
    """Send chat history with most recent user message to the chat completions API."""
    stream_results = ''
    history[-1][1] = ''
    # try:
    response = openai.ChatCompletion.create(
        model=selected_model,
        messages=[{'role':'system', 'content': system_msg}] + gradio_chat_history_to_openai_chat_completions_format(history),
        temperature=temperature,
        stream=stream  # this time, we set stream=True
    )
    if stream:
        for chunk in response:
            # model_results.append(model_results)
            # print(chunk)
            # print(chunk.get('choices',[{}])[0].get('delta',{}).get('content',''),end='')
            stream_results += chunk.get('choices',[{}])[0].get('delta',{}).get('content','')
            # history[-1][1] = parse_codeblock(stream_results) #removed because gradio properly formats code blocks now
            history[-1][1] = stream_results
            yield history
    else:
        # print(response)
        # print(response.get('choices',[{}])[0].get('message',{}).get('content',''))
        # print(parse_codeblock(response.get('choices',[{}])[0].get('message',{}).get('content','')))
        # history[-1][1] = parse_codeblock(response.get('choices',[{}])[0].get('message',{}).get('content','')) #gradio fixed code blocks natively
        history[-1][1] = response.get('choices',[{}])[0].get('message',{}).get('content','')
        # print(history)
        yield history
    # except:
    #     pass
    #     # print(history, system_msg, [{'role':'system', 'content': system_msg}] + history_to_chatgpt_format(history))

    # print(response)
    # print(stream_results)
    # print(parse_codeblock(stream_results))
    # print(history[-1][1])

# %% ../nbs/02_basic_chat_gradio.ipynb 26
def create_basic_ui():
    # model_results = []
    with gr.Blocks(title='Jarvis - My ChatGPT') as demo:
        with gr.Tab(label='Chat'):
            chatbot = gr.Chatbot()
            # chatbot.change(fn=lambda: None, scroll_to_output=True) #This also doesn't work. Autoscroll when chatbot in tab is known issue.
            with gr.Row():
                with gr.Column(scale=10):
                    msg = gr.Textbox()
                with gr.Column(scale=1):
                    clear = gr.Button("Clear")
                    submit = gr.Button("Send")
        with gr.Tab(label='Settings'):
            system_msg = gr.Textbox(value='You are a helpful assistant.', info='This is the system message for OpenAI Chat APIs.')
            model_selection = gr.Dropdown(choices=['gpt-3.5-turbo','gpt-4'],value='gpt-3.5-turbo',label='Select model: ')
            temperature = gr.Slider(maximum=2., value=0., step=.1, label='Temperature', info='What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.',)
            stream_results = gr.Checkbox(value=True, label='Stream Results', )

        submit0_kwargs = dict(fn=process_user_message, inputs=[msg, chatbot], outputs=[msg, chatbot])
        submit1_kwargs = dict(fn=process_bot_message, inputs=[chatbot, system_msg, model_selection, temperature, stream_results], outputs=chatbot)
        msg.submit(**submit0_kwargs).then(**submit1_kwargs)
        clear.click(fn=lambda: (None, None), inputs=None, outputs=[chatbot,msg], queue=False)
        submit.click(**submit0_kwargs).then(**submit1_kwargs)
    return demo

# %% ../nbs/02_basic_chat_gradio.ipynb 27
def create_and_run_basic_ui():
    demo = create_basic_ui()
    demo.queue(concurrency_count=2)
    demo.launch(server_name='0.0.0.0', inline=False)
    return demo
