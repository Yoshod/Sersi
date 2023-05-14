import nextcord
import sqlite3
import pickle
from nextcord.ext import commands
from utils.config import Configuration
from utils.perms import is_dark_mod, permcheck


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to create the Sersi Database",
    )
    async def database(self, interaction):
        pass

    @database.subcommand(
        description="Used to create the Sersi Database",
    )
    async def create(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cases
                  (id TEXT PRIMARY KEY,
                   type TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS slur_cases
                  (id TEXT PRIMARY KEY,
                   slur_used TEXT,
                   report_url TEXT,
                   offender INTEGER,
                   moderator INTEGER,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "bad_faith_ping_cases"
                  (id TEXT PRIMARY KEY,
                   report_url TEXT,
                   offender INTEGER,
                   moderator INTEGER,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS probation_cases
                  (id TEXT PRIMARY KEY,
                   offender INTEGER,
                   initial_moderator INTEGER,
                   approving_moderator INTEGER,
                   reason TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS reformation_cases
                  (id TEXT PRIMARY KEY,
                   case_number INTEGER,
                   offender INTEGER,
                   moderator INTEGER,
                   cell_id INTEGER,
                   reason TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS tickets
                (ticket_id TEXT PRIMARY KEY,
                ticket_escalation_initial TEXT,
                ticket_escalation_final TEXT,
                ticket_channel_id INTEGER,
                ticket_creator_id INTEGER,
                ticket_active BOOLEAN,
                ticket_closer_id INTEGER,
                timestamp_opened INTEGER,
                timestamp_closed INTEGER,
                priority_initial TEXT,
                priority_final TEXT,
                main_category TEXT,
                sub_category TEXT,
                related_tickets TEXT
                survey_sent BOOLEAN
                survey_score INTEGER
                survery_response TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ticket_categories
            (category TEXT PRIMARY KEY)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ticket_subcategories
            (category TEXT,
            subcategory TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS scrubbed_cases
            (id TEXT PRIMARY KEY,
            type TEXT,
            offender INTEGER,
            scrubber INTEGER,
            reason TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS notes
            (id TEXT PRIMARY KEY,
            noted INTEGER,
            noter INTEGER,
            note TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS warn_cases
            (id TEXT PRIMARY KEY,
            offender INTEGER,
            moderator INTEGER,
            offence TEXT,
            details TEXT,
            active BOOLEAN,
            timestamp INTEGER,
            deactive_reason TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS warn_adjustments
            (id TEXT PRIMARY KEY,
            adjustor INTEGER,
            original_offence TEXT,
            new_offence TEXT,
            offence_adjusted TEXT,
            original_details TEXT,
            new_details TEXT,
            details_adjusted BOOLEAN,
            original_deactive_reason TEXT,
            new_deactive_reason TEXT,
            reason TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS timeout_cases
            (id TEXT PRIMARY KEY,
            offender INTEGER,
            moderator INTEGER,
            offence TEXT,
            details TEXT,
            planned_end INTEGER,
            actual_end INTEGER,
            adjusted BOOLEAN,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS timeout_adjustments
            (id TEXT PRIMARY KEY,
            adjustor INTEGER,
            original_planned_end INTEGER,
            new_planned_end INTEGER,
            end_adjusted BOOLEAN,
            original_offence TEXT,
            new_offence TEXT,
            offence_adjusted BOOLEAN,
            original_offence_details TEXT,
            new_offence_details TEXT,
            offence_details_adjusted BOOLEAN
            adjustment_reason TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS kick_cases
            (id TEXT PRIMARY KEY,
            offender INTEGER,
            moderator INTEGER,
            reason TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS kick_adjustments
            (id TEXT PRIMARY KEY,
            adjustor INTEGER,
            original_reason TEXT,
            new_reason TEXT,
            reason TEXT,
            timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ban_cases
            (id TEXT PRIMARY KEY,
            vote_url TEXT,
            offender INTEGER,
            moderator INTEGER,
            offence TEXT,
            details TEXT,
            ban_type TEXT,
            timestamp INTEGER,
            reviewer TEXT,
            review_outcome TEXT,
            review_comment TEXT,
            active BOOLEAN,
            unban_reason TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS offences
            (offence TEXT PRIMARY KEY,
            first_instance TEXT,
            second_instance TEXT,
            third_instance TEXT,
            detail TEXT)"""
        )

        conn.commit()

        conn.close()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the category tables",
    )
    async def ticket_categories(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO ticket_categories (category) VALUES ('technical'), ('policy'), ('report'), ('complaint'), ('appeal'), ('other');"""
        )

        cursor.execute(
            """INSERT INTO ticket_subcategories (category, subcategory)
                VALUES
                ('Technical', 'Altdentifier Verification'),
                ('Technical', 'Bot Not Working'),
                ('Technical', 'User Permission Problem'),
                ('Technical', 'Other Technical Issue'),
                ('Policy', 'User Conduct Query'),
                ('Policy', 'Moderation Policy Query'),
                ('Policy', 'Terms of Service Query'),
                ('Policy', 'Other Policy Query'),
                ('Report', 'Message Report'),
                ('Report', 'User Report'),
                ('Report', 'Channel Report'),
                ('Report', 'Forum Post Report'),
                ('Report', 'Thread Report'),
                ('Report', 'Voice Chat Report'),
                ('Report', 'Other Report'),
                ('Complaint', 'Verification Support Complaint'),
                ('Complaint', 'Event Manager Complaint'),
                ('Complaint', 'Community Engagement Team Complaint'),
                ('Complaint', 'Community Engagement Team Lead Complaint'),
                ('Complaint', 'Trial Moderator Complaint'),
                ('Complaint', 'Moderator Complaint'),
                ('Complaint', 'Senior Moderator Complaint'),
                ('Complaint', 'Mega Administrator Complaint'),
                ('Complaint', 'Other Complaint'),
                ('Appeal', 'Ban Appeal'),
                ('Appeal', 'Timeout Appeal'),
                ('Appeal', 'Other Appeal'),
                ('Other', 'Business Suggestion for Adam'),
                ('Other', 'Adult Access Verification'),
                ('Other', 'Adult Access Denial Query'),
                ('Other', 'Other Issue');"""
        )

        conn.commit()

        conn.close()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the offences table",
    )
    async def offence_fill(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO offences (offence, first_instance, second_instance, third_instance, detail)
            VALUES
            ('Intentional Bigotry', 'Priority Ban', 'Priority Ban', 'Priority Ban', 'Intentional bigotry refers to acts of discrimination, prejudice, or intolerance that are committed purposefully and with the intent to harm or marginalise a particular group of people. This can include hate speech, racial slurs, or other forms of derogatory language, as well as actions that exclude or discriminate against individuals based on their race, ethnicity, gender, sexual orientation, religion, or other personal characteristics.'),

            ('Unintentional Bigotry', 'Informal Warning', 'Warning', 'Reformation Centre', 'Unintentional bigotry refers to instances of discrimination, prejudice, or intolerance that are committed without the intent to harm or marginalise a particular group of people. It can occur when individuals make assumptions or use language that is insensitive or unaware of the experiences and perspectives of marginalised groups. This can include making jokes or comments that perpetuate stereotypes, or failing to recognise the impact of systemic discrimination on certain individuals or communities.'),

            ('Tier 1 NSFW', 'Informal Warning', 'Warning', 'Warning', 'The lowest tier of NSFW Content is content which is suggestive in nature. It may not show anything explicit, but it is so heavily suggested that you would have to be incredibly dense to not notice it.'),

            ('Tier 2 NSFW', 'Informal Warning', 'Warning', 'Warning', 'The second tier of NSFW content, this is content which is explicit in nature, but not pornographic. This could be images in which genitals are clearly visible, or referring to sex acts.'),

            ('Tier 3 NSFW', 'Warning', 'Warning', 'Temporary Ban', 'This is porn. Content generally made for the purposes of arousing others. There is no excuse for posting this type of content.'),

            ('Tier 4 NSFW', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'This is child sexual abuse material.'),

            ('Tier 1 NSFL', 'Warning', 'Warning', 'Warning', 'This is mild gore or violence that is not too disturbing. This can be posted with a spoiler tag and appropriate warnings.'),

            ('Tier 2 NSFL', 'Warning', 'Warning', 'Warning', 'This is moderate gore or violence that is somewhat disturbing. Still within the range of a person of average firmness. This can be posted with a spoiler tag, appropriate warnings, and in a channel specified as NSFW.'),

            ('Tier 3 NSFL', 'Warning', 'Temporary Ban', 'Priority Ban', 'This is severe gore or violence and includes depictions of severely graphic injuries, or death. This may also be content that is extremely violent or disturbing. This does not belong on ASC.'),

            ('Tier 4 NSFL', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'This is extreme gore or violence that is so graphic or disturbing it could cause trauma to those who see it. This may include torture, mutilation, decapitation, or dismemberment. This should be reported to Discord Trust and Safety.'),

            ('Regressive/Hateful/Harmful Message', 'Reformation Centre', 'Reformation Centre', 'Reformation Centre', 'This is any message that promotes or supports ideas, beliefs, or behaviours that are discriminatory, prejudiced, or harmful to individuals or groups. This can include messages that are offensive derogatory, or threatening towards others, or that seek to incite or justify hate speech or violence'),

            ('Channel/Bot Misuse', 'Informal Warning', 'Warning', 'Warning', 'This is using a bot or channel for any purpose other than it was intended to be used for.'),

            ('Discussion in Foreign Language', 'Informal Warning', 'Warning', 'Warning', 'This is engaging in a series of messages back and forth in any language other than English.'),

            ('Spamming', 'Informal Warning', 'Warning', 'Warning', 'This is any kind of unwanted or repetitive message that is not related to the current conversation or topic at hand. This can include flooding the chat with repetitive messages, posting the same message multiple times, or sending unsolicited advertisements or links. '),

            ('Harassment/Bullying', 'Warning', 'Reformation Centre', 'Priority Ban', 'This is any repeated behaviour that is intended to cause harm, humiliation, or distress to an individual'),

            ('Disclosing Personally Identifying Information', 'Priority Ban', 'Priority Ban', 'Priority Ban', 'Personally Identifying Information is any information relating to a person who can be identified or who are identifiable, directly from the information in question or who can be indirectly identified from that information in combination with other information.'),

            ('Impersonating Adam Something', 'Warning', 'Emergency Ban', 'Emergency Ban', 'This is when a user pretends to be Adam Something.'),

            ('Impersonating Server Staff', 'Warning', 'Emergency Ban', 'Emergency Ban', 'This is when a user pretends to be a staff member on Adam Something Central. They may either be impersonating a specific staff member, or just pretending to have permissions they do not have.'),

            ('Impersonating Discord Staff', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'This is when a user pretends to be a member of Discord Staff. This should be reported to Discord Trust and Safety.'),

            ('Scamming', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'This is when a user attempts to deceive or defraud an individual for their own gain.'),

            ('Advertising Outside Shillposting', 'Warning', 'Warning', 'Priority Ban', 'When a user shillposts outside of shillposting.'),

            ('Failure to Disclose in Shillposting', 'Warning', 'Warning', 'Priority Ban', 'When a user does not disclose that they benefit directly from what they are shilling.'),

            ('Bad Faith Engagement', 'Informal Warning', 'Warning', 'Reformation Centre', 'When a user debates or argues in bad faith, they do not care about what is right or wrong but about winning the argument.'),

            ('Posting Classified Material', 'Priority Ban', 'Priority Ban', 'Priority Ban', 'This is posting any information that is legally classified by a national government. Even if this information is leaked, if it remains legally classified it should not be posted.'),

            ('Posting Copyrighted Material', 'Warning', 'Warning', 'Priority Ban', 'This is when a user posts materials they do not have the rights to and the usage does not qualify under fair usage.'),

            ('Begging', 'Informal Warning', 'Warning', 'Warning', 'This is when a user requests or begs for nitro, money, or something else.'),

            ('Auto-Moderation Circumvention', 'Informal Warning', 'Warning', 'Warning', 'This is when a user attemps to bypass auto-moderation features on the server.'),

            ('Unauthorised Access', 'Emergency Ban', 'Emergency Ban', 'Emergency Ban', 'This is when a user attempts to gain access to a bot on ASC they do not have permission to access. This includes running commands they do not have permission to run.'),

            ('Threatening Behaviour', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'Emergency Ban & TnS Report', 'This is when a user makes a credible threat against another user. This should always be reported to Discord Trust and Safety.'),

            ('Acting Contrary to Moderator Commands', 'Informal Warning', 'Warning', 'Warning', 'This is when a user fails to listen to the commands of a moderator.'),

            ('Nuisance in VC', 'Informal Warning', 'Warning', 'Warning', 'This is when somebody is being annoying in VC either by using a soundboard, making noises, joining and leaving constantly, or any other behaviour.'),

            ('Riling Up', 'Warning', 'Warning', 'Reformation Centre', 'This is when a user attempts to foment anger or resentment against the ASC moderation team.'),

            ('Complaining About Moderator Action', 'Informal Warning', 'Warning', 'Warning', 'This is when a user publicly complains about a moderation action taken against them rather than appealing it via a ticket.'),

            ('Moderator Decision Circumvention', 'Warning', 'Warning', 'Warning', 'This is when a user attempts to circumvent a decision, such as moderator shopping.'),

            ('Posting Seizure Enducing Content', 'Emergency Ban', 'Emergency Ban', 'Emergency Ban', 'This when a user posts content that is designed to enduce a seizure to those with photosensitive epilepsy.'),

            ('Other', NULL, NULL, NULL, 'For any offence currently not covered by the existing list of offences.');"""
        )

        conn.commit()

        conn.close()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to migrate case data",
    )
    async def case_migration(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        # Load the first pickle file containing the case data
        with open(self.config.datafiles.casehistory, "rb") as f:
            cases_dict = pickle.load(f)

        # Load the second pickle file containing the case details
        with open(self.config.datafiles.casedetails, "rb") as f:
            details_dict = pickle.load(f)

        for __, case_list in cases_dict.items():
            for case in case_list:
                case_id, case_type, timestamp = case
                # Ignore Anonymous Message Mute cases
                if case_type == "Anonymous Message Mute":
                    continue
                # Insert the case into the cases table
                cursor.execute(
                    "INSERT INTO cases VALUES (?, ?, ?)",
                    (case_id, case_type, timestamp),
                )
                # Process the case details
                if case_id in details_dict:
                    details_list = details_dict[case_id]
                    case_type = details_list[0]
                    if case_type == "Bad Faith Ping":
                        report_url, offender_id, moderator_id, timestamp = details_list[
                            1:
                        ]
                        cursor.execute(
                            "INSERT INTO bad_faith_ping_cases VALUES (?, ?, ?, ?, ?)",
                            (case_id, offender_id, report_url, moderator_id, timestamp),
                        )
                    elif case_type == "Probation":
                        (
                            offender_id,
                            primary_moderator_id,
                            secondary_moderator_id,
                            reason,
                            timestamp,
                        ) = details_list[1:]
                        cursor.execute(
                            "INSERT INTO probation_cases VALUES (?, ?, ?, ?, ?, ?)",
                            (
                                case_id,
                                offender_id,
                                primary_moderator_id,
                                secondary_moderator_id,
                                reason,
                                timestamp,
                            ),
                        )
                    elif case_type == "Reformation":
                        (
                            case_number,
                            offender_id,
                            moderator_id,
                            channel_id,
                            reason,
                            timestamp,
                        ) = details_list[1:]
                        cursor.execute(
                            "INSERT INTO reformation_cases VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (
                                case_id,
                                case_number,
                                offender_id,
                                moderator_id,
                                channel_id,
                                reason,
                                timestamp,
                            ),
                        )
                    elif case_type == "Slur Usage":
                        (
                            slur_used,
                            report_url,
                            offender_id,
                            moderator_id,
                            timestamp,
                        ) = details_list[1:]
                        cursor.execute(
                            "INSERT INTO slur_cases VALUES (?, ?, ?, ?, ?, ?)",
                            (
                                case_id,
                                slur_used,
                                report_url,
                                offender_id,
                                moderator_id,
                                timestamp,
                            ),
                        )

        conn.commit()
        conn.close()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")


def setup(bot, **kwargs):
    bot.add_cog(Database(bot, kwargs["config"]))
