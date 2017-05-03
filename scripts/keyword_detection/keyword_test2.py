#https://pypi.python.org/pypi/pocketsphinx

import os
import vocalize

from pocketsphinx import LiveSpeech, get_model_path
def get_sphinx():
    model_path = './model'
    speech = LiveSpeech(
        verbose=True,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'en-us/en-us'),
        lm=os.path.join(model_path, 'robot_names.lm'),
        dic=os.path.join(model_path, 'robot_names.dic')
    )
    return speech

    for ps in speech:
        print(ps.segments())
        print('Detailed segments:', *ps.segments(detailed=True), sep='\n')


 def background_listening(recognizer, audio):
     try:
         speech_input = get_sphinx()

         for phrase in speech_input:
             print "I HEARD" + phrase
             if not phrase in bots:
                 continue
             bots_addressed = get_bots(phrase)
             if bots_addressed:
                 wake_up_response = get_wake_up_response(bots_addressed)
                 print "vocalizing" + wake_up_response
                 vocalize.play_text_to_speech(wake_up_response)
                 while pygame.mixer.get_busy():
                     print "audio is playing"
                     pass
                 m = sr.Microphone()
                 with m as source:
                     audio = recognizer.listen(source)
                 try:
                     query = recognizer.recognize_google(audio)
                 except IndexError:
                     print "No internet connection"
                 if query:
                     print "google heard: " + query
                     if protocol == 'UDP':
                         message = query + "|" + response_ip + "|" + str(response_port)
                         print message
                         for bot_name in bots_addressed:
                             server_ip, server_port = robot_to_info[bot_name]
                             print "Sending command to: %s" % bot_name
                             send_udp_message(server_ip, server_port, message)

         except sr.UnknownValueError:
             pass # Sound were not intelligible speech
         except sr.RequestError:
             print "had an issue..."
