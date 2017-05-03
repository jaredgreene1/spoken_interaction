#https://pypi.python.org/pypi/pocketsphinx

import os
import vocalize
import speech_recognition as sr
import pyaudio

from pocketsphinx import LiveSpeech, get_model_path, Decoder
def get_sphinx():
    config = Decoder.default_config()

    model_path = './model'
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'en-us/en-us'),
        lm=os.path.join(model_path, 'robot_names.lm'),
        dic=os.path.join(model_path, 'robot_names.dic')
    )
    print "Sphinx listener created"
    return speech

    for ps in speech:
        print(ps.segments())

def decoder():
    # Init decoder
    print 5

    config = Decoder.default_config()
    config.set_string('-hmm', './model/en-us/en-us')
    config.set_string('-dict', './model/robot_names.dic')
    decoder = Decoder(config)
    # Add searches
    decoder.set_kws('robot_names', './model/robot_names.list')
    print 5

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    stream.start_stream()

    in_speech_bf = False
    decoder.start_utt()
    print 5
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
            if decoder.get_in_speech() != in_speech_bf:
                in_speech_bf = decoder.get_in_speech()
                if not in_speech_bf:
                    decoder.end_utt()

                    # Print hypothesis and switch search to another mode
                    print 'Result:', decoder.hyp().hypstr
                    #
                    # if decoder.get_search() == 'keyword':
                    #      decoder.set_search('lm')
                    # else:
                    #      decoder.set_search('keyword')

                    # decoder.start_utt()
        else:
            break
    decoder.end_utt()




if __name__=='__main__':
    decoder()


def background_listening(bots):
    try:
        decoder()
        # speech_input = get_sphinx()
        # print "I'm searching for "
        # print bots
        # for phrase in speech_input:
        #     print "I HEARD " + str(phrase)
        #     if not phrase in bots:
        #         print "I don't care about that bot"
        #         continue
        #     bots_addressed = get_bots(phrase)
        #     if bots_addressed:
        #         wake_up_response = get_wake_up_response(bots_addressed)
        #         print "vocalizing" + wake_up_response
        #         vocalize.play_text_to_speech(wake_up_response)
        #         while pygame.mixer.get_busy():
        #             print "audio is playing"
        #             pass
        #         m = sr.Microphone()
        #         with m as source:
        #             audio = recognizer.listen(source)
        #         try:
        #             query = recognizer.recognize_google(audio)
        #         except IndexError:
        #              print "No internet connection"
        #         if query:
        #             print "google heard: " + query
        #             if protocol == 'UDP':
        #                 message = query + "|" + response_ip + "|" + str(response_port)
        #                 print message
        #                 for bot_name in bots_addressed:
        #                     server_ip, server_port = robot_to_info[bot_name]
        #                     print "Sending command to: %s" % bot_name
        #                     send_udp_message(server_ip, server_port, message)
    except sr.UnknownValueError:
        pass # Sound were not intelligible speech
    except sr.RequestError:
        print "had an issue..."
