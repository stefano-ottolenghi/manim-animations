from manim import *
from numpy import sin, cos, sign, sum
from random import random

#config.background_color = WHITE
# manim -pql -s drivers_result.py

class Result(Scene):
    caption = None

    def construct(self):
        ## headings
        headerT = UP*3
        #dbT = Text('DATABASE').move_to(headerT + RIGHT*5)
        dbT = SVGMobject('database.svg').set_color(WHITE).scale(0.5).move_to(headerT + RIGHT*5)
        appT = Text('App').move_to(headerT + LEFT*4.5)
        driverT = Text('Driver').move_to(headerT + LEFT*2)
        self.add(dbT)
        self.add(appT)
        self.add(driverT)
        # TODO add CLIENT and SERVER and draw shallow line

        ## query from app to db
        queryT = Text('Query')
        self.add(queryT.next_to(appT, DOWN, buff=MED_LARGE_BUFF))
        self.describe(Text('The application crafts a Cypher query.'))
        self.wait()
        self.play(queryT.animate.move_to((driverT.get_x(), queryT.get_y(), 0)))
        query_box = SurroundingRectangle(queryT, buff=SMALL_BUFF, color=YELLOW)
        self.describe(Text('The driver sends it to the Neo4j server through Bolt.'))
        self.play(Create(query_box))
        self.wait()
        query = VGroup(queryT, query_box)
        self.play(query.animate.move_to((dbT.get_x(), queryT.get_y(), 0)))
        self.play(FadeOut(query_box))

        ## db loading
        loader = Dot(radius=0.05).next_to(dbT, RIGHT)
        path = Circle(0.25).flip().next_to(dbT, RIGHT)
        self.play(FadeOut(queryT, target_position=dbT.get_bottom(), scale=1), run_time=1)
        self.play(MoveAlongPath(loader, path), rate_func=smooth, run_time=1)
        self.play(MoveAlongPath(loader, path), rate_func=smooth, run_time=1)
        self.play(FadeOut(loader))

        ## records stream from db to driver
        record_size = (0.4, 0.3)
        record_big_size = (4, 1)
        total_records = 45
        driver_buf_size = 25
        ncols = 5
        nrows = driver_buf_size/ncols
        #TODO align driver_buf better
        driver_buf = Rectangle(width=record_size[0]*ncols, height=record_size[1]*nrows).move_to((driverT.get_x(), queryT.get_y(), 0))
        anims = []
        for i in range(total_records):
            # TODO records build a mountain
            # record under db
            recordT = Text(f'#{i}').set_z_index(i+1)  # z index for rectangle fill
            record_box = Rectangle(width=record_size[0], height=record_size[1], color=WHITE, fill_color=BLACK, fill_opacity=0.8).set_z_index(i)
            recordT.scale_to_fit_width(record_box.width-0.1)
            pos = RIGHT*5 + sign(random()-0.5)*LEFT*random() + sign(random()-0.5)*UP*random()
            record_db = VGroup(recordT, record_box).move_to(pos)#.rotate(PI*random()*0.1)

            if i < driver_buf_size:
                # record in driver buffer
                buff_pos = (driver_buf.get_left()[0], driver_buf.get_top()[1], 0.0)
                recordT = Text(f'#{i}')
                record_box = Rectangle(width=record_size[0], height=record_size[1], color=WHITE)
                recordT.scale_to_fit_width(record_box.width-0.1)  # some padding
                if i < 10: recordT.scale(0.7)  # double digits take more space than single
                record_buff = VGroup(recordT, record_box).align_to(driver_buf, LEFT+UP)
                record_buff.set_z_index(i)
                pos_in_buff = record_buff.get_center() + RIGHT*(i%(ncols))*record_box.width + DOWN*((i//(ncols)))*record_box.height
                record_buff.move_to(pos_in_buff)

                # animate record from db to driver
                anim = AnimationGroup(GrowFromPoint(record_db, dbT.get_center()),
                        record_db.animate.become(record_buff))
            else:
                # animate record from db only
                anim = AnimationGroup(GrowFromPoint(record_db, dbT.get_center()))

            anims.append(anim)

        self.play(FadeIn(driver_buf), LaggedStart(*anims, lag_ratio=0.25))

        self.wait()

    def describe(self, text):
        caption_pos = DOWN*3
        text.move_to(caption_pos)
        text.scale(0.3)
        if self.caption == None:
            self.play(Write(text), run_time=0.5)
        else:
            self.play(Transform(self.caption, text))
        self.caption = text