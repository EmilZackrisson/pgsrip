class ASSItem:
    def __init__(self, text, start_time, end_time, pos_x=None, pos_y=None) -> None:
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.pos_x = pos_x
        self.pos_y = pos_y


class ASSCreator:
    def __init__(self, title="Generated Subtitles", resolution_x=1920, resolution_y=1080):
        """
        Initializes the ASS creator with necessary headers and a default style.
        Resolution sets the coordinate space for positioning (default is 1080p).
        """
        self.title = title
        self.res_x = resolution_x
        self.res_y = resolution_y
        self.events = []
        self.header = self._generate_header()

    def _generate_header(self):
        """Generates the required ASS boilerplate headers."""
        return f"""[Script Info]
Title: {self.title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: {str(self.res_x).split('.')[0]}
PlayResY: {str(self.res_y).split('.')[0]}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def _format_time(self, time_str):
        """Converts SRT time (00:00:02,920) to strict ASS time (0:00:02.92)."""
        # 1. Swap comma for a dot
        time_str = str(time_str).replace(',', '.')

        # 2. Split into base time and decimals
        if '.' in time_str:
            base_time, decimals = time_str.split('.')
            # Force exactly 2 decimal places by slicing the string
            centiseconds = decimals[:2]
        else:
            base_time = time_str
            centiseconds = "00"

        # 3. ASS format requires the hour to be a single digit if it's less than 10
        # e.g., "00:00:02" becomes "0:00:02"
        if base_time.startswith("00:"):
            base_time = "0:" + base_time[3:]
        elif base_time.startswith("0"):
            base_time = base_time[1:]  # Changes "01:..." to "1:..."

        return f"{base_time}.{centiseconds}"

    def add_subtitle(self, text, start_time, end_time, pos_x=None, pos_y=None):
        """
        Adds a single subtitle event.

        :param text: The text to display.
        :param start_time: Start time in 'H:MM:SS.cc' format.
        :param end_time: End time in 'H:MM:SS.cc' format.
        :param pos_x: X coordinate for positioning (optional).
        :param pos_y: Y coordinate for positioning (optional).
        """
        start_time = self._format_time(start_time)
        end_time = self._format_time(end_time)

        # ASS expects 2 decimal places (centiseconds), but most players accept 3.
        # We'll leave it as is after swapping the comma for a dot.

        # Fix line breaks: replace literal newlines with the \N tag
        clean_text = text.replace('\n', '\\N').replace('\r', '')

        # 3. Handle positioning and alignment
        if pos_x is not None and pos_y is not None:
            # Added \an7 to force Top-Left alignment to match PGS coordinates
            position_tag = f"{{\\an7\\pos({pos_x},{pos_y})}}"
        else:
            position_tag = ""

        # 4. Format and append the dialogue string
        dialogue = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{clean_text}"
        self.events.append(dialogue)

    def add_item(self, ass_item: ASSItem):
        self.add_subtitle(ass_item.text, ass_item.start_time, ass_item.end_time, ass_item.pos_x, ass_item.pos_y)

    def save(self, filepath):
        """Writes the generated ASS content to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.header)
                for event in self.events:
                    f.write(event + '\n')
            print(f"Successfully saved subtitles to {filepath}")
        except IOError as e:
            print(f"Error saving file: {e}")
