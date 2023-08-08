def filter_course(df, coursecode, coursename, credit, prerequisite, semester):
    return df[
        df['Course Code'].astype(str).str.contains(coursecode) &
        df['Name'].astype(str).str.contains(coursename) &
        df['AUs'].astype(str).str.contains(credit) &
        df['Related Courses'].astype(str).str.contains(prerequisite) &
        df['Semester Offered'].astype(str).str.contains(semester)
    ]