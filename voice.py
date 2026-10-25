import speech_recognition as sr


def listen_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\nListening... Please speak clearly.")

        # Background noise ko adjust karega
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

            print("Processing voice...")

            command = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            command = command.lower().strip()

            print("Command:", command)

            return command

        except sr.WaitTimeoutError:
            print("No voice detected.")
            return ""

        except sr.UnknownValueError:
            print("Could not understand the voice.")
            return ""

        except sr.RequestError as e:
            print("Speech recognition service error:", e)
            return ""

        except Exception as e:
            print("Voice Error:", e)
            return ""


if __name__ == "__main__":
    command = listen_command()
    print("Final Command:", command)