from manim import *
from numpy import sin, cos, sign, sum
from random import random

#config.background_color = WHITE
# manim -pql -s drivers_result.py

class Result(Scene):
    caption = None
    animations_queue = []

    def construct(self):
        ## headings
        headerT = UP*3
        #dbT = Text('DATABASE').move_to(headerT + RIGHT*5)
        dbT = SVGMobject('database.svg').set_color(WHITE).scale(0.5).move_to(headerT + RIGHT*4)
        appT = Text('App').move_to(headerT + LEFT*4)
        driverT = Text('Driver').move_to(headerT + LEFT*0.5)
        divider = DashedLine((2, dbT.get_y(), 0), (2, -1, 0)).set_opacity(0.5)
        clientT = Text('CLIENT').scale(0.5).align_to(config.left_side, LEFT).rotate(PI/2)
        serverT = Text('SERVER').scale(0.5).align_to(config.right_side, RIGHT).rotate(-PI/2)
        self.add(dbT, appT, driverT, divider, clientT, serverT)

        # TODO add CLIENT and SERVER and draw shallow line
        #return
        ## query from app to db
        queryT = Text('Query')
        self.add(queryT.next_to(appT, DOWN, buff=LARGE_BUFF))
        self.describe(Text('Your application crafts a Cypher query.'))
        self.wait()
        self.play(queryT.animate.move_to((driverT.get_x(), queryT.get_y(), 0)))
        query_box = SurroundingRectangle(queryT, buff=SMALL_BUFF, color=YELLOW)
        self.describe(Text('The driver sends it to the Neo4j server through the Bolt protocol.'))
        self.play(Create(query_box), run_time=0.8)
        query = VGroup(queryT, query_box)
        self.play(query.animate.move_to((dbT.get_x(), queryT.get_y(), 0)), run_time=0.8)

        ## db loading
        self.describe(Text('The database fetches the result.'))
        loader = Dot(radius=0.05).next_to(dbT, RIGHT)
        path = Circle(0.25).flip().next_to(dbT, RIGHT)
        self.play(FadeOut(query_box), FadeOut(queryT, target_position=dbT.get_bottom(), scale=1), run_time=0.5)
        self.play(MoveAlongPath(loader, path), rate_func=smooth, run_time=0.8)
        self.play(MoveAlongPath(loader, path), rate_func=smooth, run_time=0.8)
        self.play(FadeOut(loader), run_time=0.5)

        content_y = 0

        ## records stream from db to driver
        record_size = (0.4, 0.3)
        record_big_size = (4, 1)
        total_records = 50
        driver_buf_size = 25
        ncols = 5
        nrows = int(driver_buf_size/ncols)
        #TODO align driver_buf better
        driver_buf = Rectangle(width=record_size[0]*ncols, height=record_size[1]*nrows).move_to((driverT.get_x(), content_y, 0))
        records_in_driver_buff = []
        records_in_db_buff = []
        anims_to_driver_buff = []
        anims_to_db_buff = []

        '''def fill_driver_buff(records_in_driver_buff, source_record, target_record):
            target_record = target_record.align_to(driver_buf, LEFT+UP)
            i = len(records_in_driver_buff)
            #target_record.set_z_index(i)
            pos_in_buff = target_record.get_center() + RIGHT*(i%(ncols))*record_size[0] + DOWN*((i//(ncols)))*record_size[1]
            target_record.move_to(pos_in_buff)

            records_in_driver_buff.append(target_record)

            # animate record from db to driver
            return AnimationGroup(
                GrowFromPoint(source_record, dbT.get_center()),
                ReplacementTransform(source_record, target_record)
            )'''

        for i in range(total_records):
            # TODO records build a mountain
            # record under db
            recordT = Text(f'#{i}').set_z_index(i+1)  # z index for rectangle fill
            record_box = Rectangle(width=record_size[0], height=record_size[1], color=WHITE, fill_color=BLACK, fill_opacity=0.8).set_z_index(i)
            recordT.scale_to_fit_width(record_box.width-0.1)
            pos = (dbT.get_x(), content_y, 0) + self.rand_displacement()
            record_db = VGroup(recordT, record_box).move_to(pos)#.rotate(PI*random()*0.1)

            if i < driver_buf_size:
                # record in driver buffer
                #buff_pos = (driver_buf.get_left()[0], driver_buf.get_top()[1], 0.0)
                recordT = Text(f'#{i}').set_z_index(i+1)
                record_box = Rectangle(width=record_size[0], height=record_size[1], color=WHITE, fill_color=BLACK, fill_opacity=0.8).set_z_index(i)
                recordT.scale_to_fit_width(record_box.width-0.1)  # some padding
                if i < 10: recordT.scale(0.7)  # double digits take more space than single
                record_buff = VGroup(recordT, record_box).align_to(driver_buf, LEFT+UP)
                #target_record.set_z_index(i)
                pos_in_buff = record_buff.get_center() + RIGHT*(i%(ncols))*record_size[0] + DOWN*((i//(ncols)))*record_size[1]
                record_buff.move_to(pos_in_buff)

                records_in_driver_buff.append(record_buff)

                # animate record from db to driver
                anim = AnimationGroup(
                    GrowFromPoint(record_db, dbT.get_center()),
                    ReplacementTransform(record_db, record_buff)
                )
                anims_to_driver_buff.append(anim)
            else:
                records_in_db_buff.append(record_db)
                # animate record from db only
                anim = AnimationGroup(GrowFromPoint(record_db, dbT.get_center()))
                anims_to_db_buff.append(anim)

        self.describe(Text('As soon as results are ready, Neo4j sends them over to the driver.\nResults are stored in a buffer until your application asks for them.'))
        self.play(FadeIn(driver_buf), LaggedStart(*anims_to_driver_buff, lag_ratio=0.25))

        self.describe(Text('When the driver buffer is full, further records wait on the server-side.'))
        self.play(LaggedStart(*anims_to_db_buff, lag_ratio=0.25))

        self.describe(Text('As soon as some records are available in the driver buffer, your application cat fetch them.\nThe server can continue fetching more results.'))
        app_action_next = Text('next()').scale(0.8).next_to(appT, DOWN, buff=0.5)
        # self.play(FadeIn(app_action), enqueue=True)
        self.play(Indicate(app_action_next), records_in_driver_buff[0].animate.move_to((appT.get_x(), content_y, 0) + self.rand_displacement(0.3)))
        self.wait()
        self.play(Indicate(app_action_next), records_in_driver_buff[1].animate.move_to((appT.get_x(), content_y, 0) + self.rand_displacement(0.3)))
        self.wait()
        app_action_fetch = Text('fetch()').scale(0.8).next_to(appT, DOWN, buff=0.5)
        anims = [r.animate.move_to((appT.get_x(), content_y, 0) + self.rand_displacement(0.3)) for r in records_in_driver_buff[2:-5]]
        self.play(ReplacementTransform(app_action_next, app_action_fetch), run_time=0.3)
        self.play(Indicate(app_action_fetch), LaggedStart(*anims, lag_ratio=0.25))
        self.play(FadeOut(app_action_fetch), run_time=0.3)

        self.describe(Text('When few records are left in the driver buffer, the driver fetches more from the server queue.'))
        last_row = VGroup(*records_in_driver_buff[-5:])
        next_batch = records_in_db_buff[:driver_buf_size-len(last_row)]
        records_in_driver_buff = records_in_driver_buff[-len(last_row):]
        anims_to_driver_buff = []
        for record in next_batch:
            i = int(record[0].original_text[1:])
            recordT = Text(f'#{i}').set_z_index(i+1)
            record_box = Rectangle(width=record_size[0], height=record_size[1], color=WHITE, fill_color=BLACK, fill_opacity=0.8).set_z_index(i)
            recordT.scale_to_fit_width(record_box.width-0.1)  # some padding
            record_buff = VGroup(recordT, record_box).align_to(driver_buf, LEFT+UP)
            #target_record.set_z_index(i)
            i += len(last_row)
            pos_in_buff = record_buff.get_center() + RIGHT*(i%(ncols))*record_size[0] + DOWN*(((i//ncols)%nrows))*record_size[1]
            record_buff.move_to(pos_in_buff)

            records_in_driver_buff.append(record_buff)

            # animate record from db to driver
            anim = ReplacementTransform(record, record_buff)
            anims_to_driver_buff.append(anim)

        self.play(
            last_row.animate.align_to(driver_buf,LEFT+UP),
            LaggedStart(*anims_to_driver_buff, lag_ratio=0.25)
        )

        self.describe(Text('If .consume() is called at any point, all results in driver and server buffers are discarded and the server \nsends the summary of results. Only what your app had fetched and stored is retained.'))
        app_action_consume = Text('consume()').scale(0.8).next_to(appT, DOWN, buff=0.5)
        to_discard = VGroup(*[r for r in (records_in_driver_buff + records_in_db_buff)])
        self.play(Indicate(app_action_consume), FadeOut(to_discard))
        self.wait()
        self.play(FadeOut(app_action_consume))

        self.wait(5)

    def describe(self, text):
        caption_pos = DOWN*3
        text.move_to(caption_pos)
        text.scale(0.4)
        if self.caption == None:
            self.play(Write(text), run_time=0.5, enqueue=True)
        else:
            self.play(ReplacementTransform(self.caption, text), enqueue=True)
        self.caption = text

    def app_action(self, text):
        caption_pos = DOWN*3
        text.move_to(caption_pos)
        text.scale(0.4)
        if self.caption == None:
            self.play(Write(text), run_time=0.3, enqueue=True)
        else:
            self.play(ReplacementTransform(self.caption, text), enqueue=True)
        self.caption = text


    def rand_displacement(self, factor=0.5):
        return sign(random()-factor)*LEFT*random() + sign(random()-factor)*UP*random()

    def play(self, *args, enqueue=False, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs):
        self.animations_queue += args

        if not enqueue:
            super().play(*self.animations_queue, subcaption=subcaption, subcaption_duration=subcaption_duration, subcaption_offset=subcaption_offset, **kwargs)
            self.animations_queue = []