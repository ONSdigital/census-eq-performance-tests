import collections
import itertools

from faker import Faker

import utils
from token_generator import create_token

fake = Faker('en_GB')

RELATIONSHIP_CHOICES = (
    "Husband or wife",
    "Same-sex civil partner",
    "Partner",
    "Grandparent",
    "Mother or father",
    "Step-mother or step-father",
    "Son or daughter",
    "Step-child",
    "Brother or sister",
    "Step\u2013brother or step\u2013sister",
    "Grandchild",
    "Relation - other",
    "Unrelated (including foster child)",
)


class TaskSet:
    def __init__(self, parent):
        self.parent = parent
        self.client = parent.client


class HouseholdTaskSet(TaskSet, utils.QuestionnaireMixins):
    def __init__(self, parent):
        super().__init__(parent)

        self.household_individual_count = self.parent.household_individual_count
        self.visitor_count = self.parent.visitor_count

    def start(self):
        introduction_url = self.do_launch_survey()
        what_is_your_address_url = self.do_start_questionnaire(introduction_url)
        household_and_accommodation_block_url = self.complete_who_lives_here_section(what_is_your_address_url)
        household_member_begin_section_url = self.complete_household_and_accommodation_section(household_and_accommodation_block_url)
        visitor_begin_url = self.complete_household_individual_sections(household_member_begin_section_url)
        complete_url = self.complete_visitors_section(visitor_begin_url)

        # submission
        self.do_submit(complete_url)

    def complete_who_lives_here_section(self, what_is_your_address_url):
        if self.household_individual_count:
            return utils.chain_page_calls(
                what_is_your_address_url,
                self.do_what_is_your_address,
                self.do_who_lives_here_start,
                self.do_permanent_or_family_home,
                self.do_household_composition,
                self.do_everyone_at_address_confirmation,
                self.do_overnight_visitors,
                self.do_household_relationships,
                self.do_who_lives_here_completed,
            )
        
        return utils.chain_page_calls(
            what_is_your_address_url,
            self.do_what_is_your_address,
            self.do_who_lives_here_start,
            self.do_permanent_or_family_home,
            self.do_else_permanent_or_family_home,
            self.do_overnight_visitors,
            self.do_household_relationships,
            self.do_who_lives_here_completed,
        )

    def complete_household_and_accommodation_section(self, household_and_accommodation_block_url):
        if self.household_individual_count:
            return utils.chain_page_calls(
                household_and_accommodation_block_url,
                self.do_household_and_accommodation_block,
                self.do_type_of_accommodation,
                self.do_type_of_house,
                self.do_self_contained_accommodation,
                self.do_number_of_bedrooms,
                self.do_central_heating,
                self.do_own_or_rent,
                self.do_number_of_vehicles,
                self.do_household_and_accommodation_completed,
            )

        return utils.chain_page_calls(
            household_and_accommodation_block_url,
            self.do_household_and_accommodation_block,
            self.do_type_of_accommodation,
            self.do_type_of_house,
            self.do_self_contained_accommodation,
            self.do_number_of_bedrooms,
            self.do_central_heating,
            self.do_household_and_accommodation_completed,
        )

    def complete_household_individual_sections(self, household_member_begin_section_url):
        if self.household_individual_count:
            for _ in range(0, self.household_individual_count):
                household_member_begin_section_url = utils.chain_page_calls(
                    household_member_begin_section_url,
                    self.do_household_member_begin_section,
                    self.do_details_correct,
                    self.do_over_16,
                    self.do_private_response,
                    self.do_sex,
                    self.do_date_of_birth,
                    self.do_marital_status,
                    self.do_another_address,
                    self.do_other_address,
                    self.do_address_type,
                    self.do_in_education,
                    self.do_term_time_location,
                    self.do_country_of_birth,
                    self.do_carer,
                    self.do_national_identity,
                    self.do_ethnic_group,
                    self.do_other_ethnic_group,
                    self.do_language,
                    self.do_religion,
                    self.do_past_usual_address,
                    self.do_passports,
                    self.do_disability,
                    self.do_qualifications,
                    self.do_employment_type,
                    self.do_jobseeker,
                    self.do_job_availability,
                    self.do_job_pending,
                    self.do_occupation,
                    self.do_ever_worked,
                    self.do_main_job,
                    self.do_hours_worked,
                    self.do_work_travel,
                    self.do_job_title,
                    self.do_job_description,
                    self.do_main_job_type,
                    self.do_business_name,
                    self.do_employer_business,
                    self.do_household_member_completed
                )

        return household_member_begin_section_url

    def complete_visitors_section(self, visitor_begin_url):
        if self.visitor_count:
            visitor_name_url = self.do_visitor_begin_section(visitor_begin_url)

            for _ in range(0, self.visitor_count):
                visitor_name_url = utils.chain_page_calls(
                    visitor_name_url,
                    self.do_visitor_name,
                    self.do_visitor_sex,
                    self.do_visitor_date_of_birth,
                    self.do_visitor_uk_resident,
                    self.do_visitor_address,
                    self.do_visitor_completed,
                )

            visitors_completed_url = visitor_name_url

            complete_url = self.do_visitors_completed(visitors_completed_url)
        else:
            complete_url = visitor_begin_url

        return complete_url

    def do_launch_survey(self):
        token = create_token(
            form_type_id='household',
            eq_id='census',
            region_code='GB-ENG',
            roles=[],
            variant_flags={'sexual_identity': 'false'}
        )
        url = f'/session?token={token}'
        response = self.get(url, name="/session")

        if response.status_code != 302:
            raise Exception('Got a non-302 back when authenticating session: {}'.format(response.status_code))

        return response.headers['Location']

    def do_start_questionnaire(self, url):
        return self.fill_in_page(url, '/introduction', {})

    def do_what_is_your_address(self, url):
        data = {
            'address-line-1': fake.secondary_address(),
            'address-line-2': fake.street_address(),
            'county': fake.street_name(),
            'country': fake.country(),
            'postcode': fake.postcode(),
            'town-city': fake.city()
        }

        return self.fill_in_page(url, '/what-is-your-address', data)

    def do_who_lives_here_start(self, url):
        return self.fill_in_page(url, '/who-lives-here-block', {})

    def do_permanent_or_family_home(self, url):
        data = {'permanent-or-family-home-answer': ['Yes' if self.household_individual_count else 'No']}
        return self.fill_in_page(url, '/permanent-or-family-home', data)

    def do_else_permanent_or_family_home(self, url):
        data = {'else-permanent-or-family-home-answer': ['No one lives here as their permanent home']}
        return self.fill_in_page(url, '/else-permanent-or-family-home', data)

    def do_household_composition(self, url):
        data = {}
        for idx in range(0, self.household_individual_count):
            data[f'household-{idx}-first-name'] = fake.first_name()
            data[f'household-{idx}-middle-names'] = fake.first_name()
            data[f'household-{idx}-last-name'] = fake.last_name()

        return self.fill_in_page(url, '/household-composition', data)

    def do_everyone_at_address_confirmation(self, url):
        data = {'everyone-at-address-confirmation-answer': ['Yes']}
        return self.fill_in_page(url, '/everyone-at-address-confirmation', data)

    def do_overnight_visitors(self, url):
        data = {'overnight-visitors-answer': self.visitor_count}
        return self.fill_in_page(url, '/overnight-visitors', data)

    def do_household_relationships(self, url):
        matrix_pages = collections.defaultdict(lambda: 0)
        for page_number, _ in itertools.combinations(range(0, self.household_individual_count), 2):
            matrix_pages[page_number] += 1

        for page_number, answer_count in matrix_pages.items():
            data = {
                f'household-relationships-answer-{idx}': fake.random.choice(RELATIONSHIP_CHOICES)
                for idx in range(0, answer_count)
            }
            url = self.fill_in_page(url, '/household-relationships', data)

        return url

    def do_who_lives_here_completed(self, url):
        return self.fill_in_page(url, '/who-lives-here-completed', {})

    def do_household_and_accommodation_block(self, url):
        return self.fill_in_page(url, '/household-and-accommodation-block', {})

    def do_type_of_accommodation(self, url):
        data = {'type-of-accommodation-answer': ['Whole house or bungalow']}
        return self.fill_in_page(url, '/type-of-accommodation', data)

    def do_type_of_house(self, url):
        data = {'type-of-house-answer': ['Detached']}
        return self.fill_in_page(url, '/type-of-house', data)

    def do_self_contained_accommodation(self, url):
        data = {'self-contained-accommodation-answer': ['No']}
        return self.fill_in_page(url, '/self-contained-accommodation', data)

    def do_number_of_bedrooms(self, url):
        data = {'number-of-bedrooms-answer': '2'}
        return self.fill_in_page(url, '/number-of-bedrooms', data)

    def do_central_heating(self, url):
        data = {
            'central-heating-answer': [
                'Gas',
                'Electric (include storage heaters)',
                'Oil',
                'Solid fuel (for example wood, coal)',
                'Renewable (for example solar panels)',
                'Other central heating',
                'No central heating',
            ]
        }
        return self.fill_in_page(url, '/central-heating', data)

    def do_own_or_rent(self, url):
        data = {'own-or-rent-answer': ['Owns outright']}
        return self.fill_in_page(url, '/own-or-rent', data)

    def do_number_of_vehicles(self, url):
        data = {'number-of-vehicles-answer': '2'}
        return self.fill_in_page(url, '/number-of-vehicles', data)

    def do_household_and_accommodation_completed(self, url):
        return self.fill_in_page(url, '/household-and-accommodation-completed', {})

    def do_household_member_begin_section(self, url):
        return self.fill_in_page(url, '/household-member-begin-section', {})

    def do_details_correct(self, url):
        data = {'details-correct-answer': ['Yes, this is my full name']}
        return self.fill_in_page(url, '/details-correct', data)

    def do_over_16(self, url):
        data = {'over-16-answer': ['Yes']}
        return self.fill_in_page(url, '/over-16', data)

    def do_private_response(self, url):
        data = {'private-response-answer': ['No, I do not want to request a personal form']}
        return self.fill_in_page(url, '/private-response', data)

    def do_sex(self, url):
        data = {'sex-answer': ['Male']}
        return self.fill_in_page(url, '/sex', data)

    def do_date_of_birth(self, url):
        data = {
            'date-of-birth-answer-day': '12',
            'date-of-birth-answer-month': '5',
            'date-of-birth-answer-year': '1988',
        }
        return self.fill_in_page(url, '/date-of-birth', data)

    def do_marital_status(self, url):
        data = {'marital-status-answer': ['In a registered same-sex civil partnership']}
        return self.fill_in_page(url, '/marital-status', data)

    def do_another_address(self, url):
        data = {'another-address-answer': ['Yes, an address within the UK']}
        return self.fill_in_page(url, '/another-address', data)

    def do_other_address(self, url):
        data = {
            'other-address-answer-building': '12',
            'other-address-answer-city': 'Newport',
            'other-address-answer-postcode': 'NP10 8XG'
        }
        return self.fill_in_page(url, '/other-address', data)

    def do_address_type(self, url):
        data = {
            'address-type-answer': ['Other'],
            'address-type-answer-other': 'Friends Home'
        }
        return self.fill_in_page(url, '/address-type', data)

    def do_in_education(self, url):
        data = {'in-education-answer': ['Yes']}
        return self.fill_in_page(url, '/in-education', data)

    def do_term_time_location(self, url):
        data = {'term-time-location-answer': ['Yes']}
        return self.fill_in_page(url, '/term-time-location', data)

    def do_country_of_birth(self, url):
        data = {'country-of-birth-england-answer': ['England']}
        return self.fill_in_page(url, '/country-of-birth', data)

    def do_carer(self, url):
        data = {'carer-answer': ['Yes, 1 -19 hours a week']}
        return self.fill_in_page(url, '/carer', data)

    def do_national_identity(self, url):
        data = {
            'national-identity-england-answer': ['English',
                                                    'Welsh',
                                                    'Scottish',
                                                    'Northern Irish',
                                                    'British',
                                                    'Other'],
            'national-identity-england-answer-other': 'Ind'
        }
        return self.fill_in_page(url, '/national-identity', data)

    def do_ethnic_group(self, url):
        data = {'ethnic-group-england-answer': ['Other ethnic group']}
        return self.fill_in_page(url, '/ethnic-group', data)

    def do_other_ethnic_group(self, url):
        data = {
            'other-ethnic-group-answer': ['Other'],
            'other-ethnic-group-answer-other': 'Telugu'
        }
        return self.fill_in_page(url, '/other-ethnic-group', data)

    def do_language(self, url):
        data = {'language-england-answer': ['English']}
        return self.fill_in_page(url, '/language', data)

    def do_religion(self, url):
        data = {
            'religion-answer': ['No religion',
                                'Buddhism',
                                'Hinduism',
                                'Judaism',
                                'Islam',
                                'Sikhism',
                                'Other'],
            'religion-answer-other': 'Ind'
        }
        return self.fill_in_page(url, '/religion', data)

    def do_past_usual_address(self, url):
        data = {'past-usual-address-answer': ['This address']}
        return self.fill_in_page(url, '/past-usual-address', data) 

    def do_passports(self, url):
        data = {'passports-answer': ['United Kingdom']}
        return self.fill_in_page(url, '/passports', data) 

    def do_disability(self, url):
        data = {'disability-answer': ['Yes, limited a lot']}
        return self.fill_in_page(url, '/disability', data) 

    def do_qualifications(self, url):
        data = {
            'qualifications-england-answer': ['Masters Degree', 'Postgraduate Certificate / Diploma']
        }
        return self.fill_in_page(url, '/qualifications', data)

    def do_employment_type(self, url):
        data = {'employment-type-answer': ['none of the above']}
        return self.fill_in_page(url, '/employment-type', data)

    def do_jobseeker(self, url):
        data = {'jobseeker-answer': ['Yes']}
        return self.fill_in_page(url, '/jobseeker', data)

    def do_job_availability(self, url):
        data = {'job-availability-answer': ['Yes']}
        return self.fill_in_page(url, '/job-availability', data)
 
    def do_job_pending(self, url):
        data = {'job-pending-answer': ['Yes']}
        return self.fill_in_page(url, '/job-pending', data)

    def do_occupation(self, url):
        data = {
            'occupation-answer': ['a student', 'long-term sick or disabled']
        }
        return self.fill_in_page(url, '/occupation', data)

    def do_ever_worked(self, url):
        data = {'ever-worked-answer': ['Yes']}
        return self.fill_in_page(url, '/ever-worked', data)

    def do_main_job(self, url):
        data = {'main-job-answer': ['an employee']}
        return self.fill_in_page(url, '/main-job', data)

    def do_hours_worked(self, url):
        data = {'hours-worked-answer': ['31 - 48']}
        return self.fill_in_page(url, '/hours-worked', data)

    def do_work_travel(self, url):
        data = {'work-travel-answer': ['Train']}
        return self.fill_in_page(url, '/work-travel', data)

    def do_job_title(self, url):
        data = {'job-title-answer': 'Software Engineer'}
        return self.fill_in_page(url, '/job-title', data)

    def do_job_description(self, url):
        data = {'job-description-answer': 'Development'}
        return self.fill_in_page(url, '/job-description', data)

    def do_main_job_type(self, url):
        data = {'main-job-type-answer': ['Employed by an organisation or business']}
        return self.fill_in_page(url, '/main-job-type', data)

    def do_business_name(self, url):
        data = {'business-name-answer': 'ONS'}
        return self.fill_in_page(url, '/business-name', data)

    def do_employer_business(self, url):
        data = {'employers-business-answer': 'Civil Servant'}
        return self.fill_in_page(url, '/employers-business', data)

    def do_household_member_completed(self, url):
        return self.fill_in_page(url, '/household-member-completed', {})

    def do_visitor_begin_section(self, url):
        return self.fill_in_page(url, '/visitor-begin-section', {})

    def do_visitor_name(self, url):
        data = {
            'visitor-first-name': 'Diya',
            'visitor-last-name': 'K'
        }
        return self.fill_in_page(url, '/visitor-name', data)
    
    def do_visitor_sex(self, url):
        data = {'visitor-sex-answer': ['Female']}
        return self.fill_in_page(url, '/visitor-sex', data)

    def do_visitor_date_of_birth(self, url):
        data = {
            'visitor-date-of-birth-answer-day': '4',
            'visitor-date-of-birth-answer-month': '11',
            'visitor-date-of-birth-answer-year': '2016',
        }
        return self.fill_in_page(url, '/visitor-date-of-birth', data)

    def do_visitor_uk_resident(self, url):
        data = {'visitor-uk-resident-answer': ['Yes, usually lives in the United Kingdom']}
        return self.fill_in_page(url, '/visitor-uk-resident', data)

    def do_visitor_address(self, url):
        data = {
            'visitor-address-answer-building': '309',
            'visitor-address-answer-city': 'Vizag',
            'visitor-address-answer-postcode': '530003'
        }
        return self.fill_in_page(url, '/visitor-address', data)

    def do_visitor_completed(self, url):
        return self.fill_in_page(url, '/visitor-completed', {})

    def do_visitors_completed(self, url):
        return self.fill_in_page(url, '/visitors-completed', {})

    def do_submit(self, url):
        return self.fill_in_page(url, '/confirmation', {})
