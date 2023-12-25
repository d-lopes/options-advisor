from datetime import date, datetime

import logging

class ExpiryDateGenerator:
    
    logger = logging.getLogger('ExpiryDateGenerator')

    @staticmethod
    def getDates(base_date: date = date.today(), start_week_offset: int = 0, end_week_offset: int = 1):
        
        dates = []
        
        base_time = datetime.fromordinal(base_date.toordinal())
        base_week = base_date.strftime("%W")
        start_week = int(base_week) + start_week_offset
        start_year = base_date.year
        end_week = int(base_week) + end_week_offset
        end_year = start_year
     
        # account for week number overflow at the end of tthe year
        weeks_cnt = end_week - start_week
        if (weeks_cnt < 0):
            weeks_cnt = 52 - start_week + end_week    
        
        ExpiryDateGenerator.logger.debug(f"processing weeks {start_week}/{start_year} to {end_week}/{end_year}")
        
        for week_no in range(0, weeks_cnt):
            
            ExpiryDateGenerator.logger.debug(f"adding week {week_no}")
            
            input_week = start_week + week_no
            input_year = start_year
            
            # due to potential week number overflow we need to make sure we never have a week bigger than 52
            if (input_week > 52):
                input_week = input_week - 52
                input_year = start_year + 1
            
            exp_date = date.fromisocalendar(input_year, input_week, 5)
                    
            dates.append(exp_date)
        
        return dates
