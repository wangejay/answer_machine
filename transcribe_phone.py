#!/usr/bin/env python
#coding:utf-8

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys
import pyglet
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/wangejay/Desktop/STT8k-c707fd1cd373.json"

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
from google.cloud import texttospeech

reload(sys)
sys.setdefaultencoding("utf-8")
# Audio recording parameters
#RATE = 16000
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms



class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)



    


def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    outputflag = 1
    outputflag2 = 1

    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        #print(sys.getdefaultencoding())
        #print(result)
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)
           
            if outputflag == 1: 
            	if transcript.find("你好") == -1:
            	    donothing=1
            	else: 
            	    print "電話回應:我很好的"
            	    
            	    music=pyglet.media.load('speech1.mp3')
            	    music.play()
            	    def exiter(dt):
            	        pyglet.app.exit()
            	    print "Song length is: %f" % music.duration
            	    # foo.duration is the song length
            	    pyglet.clock.schedule_once(exiter, music.duration)    
            	    pyglet.app.run()
            	    break

            if outputflag2 == 1: 	
            	if transcript.find("訂位") == -1:
            	    donothing=1
            	else: 
            	    print "電話回應:好的，你們有幾個人"
            	    
            	    music=pyglet.media.load('speech2.mp3')
            	    music.play()
            	    def exiter(dt):
            	        pyglet.app.exit()
            	    print "Song length is: %f" % music.duration
            	    # foo.duration is the song length
            	    pyglet.clock.schedule_once(exiter, music.duration)
            	    
            	    pyglet.app.run()
            	    break

                if transcript.find("個人") == -1:
                    donothing=1
                else: 
                    print "電話回應:那你的電話是多少"
                    
                    music=pyglet.media.load('speech3.mp3')
                    music.play()
                    def exiter(dt):
                        pyglet.app.exit()
                    print "Song length is: %f" % music.duration
                    # foo.duration is the song length
                    pyglet.clock.schedule_once(exiter, music.duration)
                    
                    pyglet.app.run()
                    break





        else:
            print("final: "+transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(結束|ASUS)\b', transcript, re.I):
                print('Exiting..')
                break

            if transcript.find("再見") == -1:
             	print('continue.....')
             	outputflag = 1
            else:
            	print('Exiting..')
                break

            if transcript.find("09") == -1:
                    donothing=1
            else: 
                print "電話回應:好的，訂位成功了"
                    
                music=pyglet.media.load('speech4.mp3')
                music.play()
                def exiter(dt):
                    pyglet.app.exit()
                print "Song length is: %f" % music.duration
                # foo.duration is the song length
                pyglet.clock.schedule_once(exiter, music.duration)
                
                pyglet.app.run()
                break
            #if transcript.find("你好嗎") == -1:
            #    print ""
            #else: 
            #    #print "電話回應:我很好的"
            #    
            #    music=pyglet.media.load('speech1.mp3')
            #    music.play()
            #    def exiter(dt):
            #        pyglet.app.exit()
            #    print "Song length is: %f" % music.duration
            #    # foo.duration is the song length
            #    pyglet.clock.schedule_once(exiter, music.duration+1)
            #    
            #    #pyglet.app.run()

           

            num_chars_printed = 0
            


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    #language_code = 'en-US'  # a BCP-47 language tag
    language_code = 'cmn-Hant-TW'  # a BCP-47 language tag
       

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)
        try: 	
        	responses = client.streaming_recognize(streaming_config, requests)
        except Exception as exception:
        # Output unexpected Exceptions.
        	print("exception exception exception exception exception ")

        # Now, put the transcription responses to use.
        try: 
            listen_print_loop(responses)
        except Exception as exception:
        # Output unexpected Exceptions.
        	print("Excption handle : Exceeded maximum allowed stream duration of 65 seconds")


if __name__ == '__main__':
    while True:
        main()
# [END speech_transcribe_streaming_mic]
