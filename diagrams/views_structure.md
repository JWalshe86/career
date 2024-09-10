# Dashboard Views

- **`dashboard`**:
  - **Purpose**: Renders the dashboard with unread emails.
  - **Functionality**:
    - Checks if the user is authenticated.
    - Fetches unread emails and handles authentication URL redirection if necessary.
    - Renders the `dashboard/dashboard.html` template with unread emails count and details.

- **`dashboard_searched`**:
  - **Purpose**: Renders the dashboard with searched jobs.
  - **Functionality**:
    - Handles both GET and POST requests for task submissions.
    - Displays tasks and a form for task submission.
    - Calculates and displays job status updates over different time periods (one week, two weeks, one month).
    - Renders the `dashboard/dashboard_searched.html` template with job status updates and tasks.

# Email Views

- **`get_unread_emails`**:
  - **Purpose**: Fetch unread emails for the authenticated user.
  - **Functionality**:
    - Checks if the environment is Heroku or local to determine how to load credentials.
    - Loads credentials from `TOKEN_JSON_CONTENT` environment variable (Heroku) or `token.json` file (local).
    - Creates a `Credentials` object and builds the Gmail service.
    - Fetches unread emails while excluding specific senders.
    - Parses and returns email details (date, sender, snippet) and any potential errors.

- **`email_dashboard`**:
  - **Purpose**: Render the email dashboard with unread emails.
  - **Functionality**:
    - Calls `get_unread_emails` to retrieve unread emails and handle any authentication URL redirection.
    - Calculates the count of unread emails.
    - Renders the `emails/email_dashboard.html` template with email details and unread email count.

# Jobsearch Views

- **`jobsearch_detail`**:
  - **Purpose**: Render job search detail for a specific jobsearch ID.
  - **Functionality**:
    - Requires superuser access.
    - Renders `jobs/jobsearch_detail.html` with jobsearch details if the user is a superuser.
    - Redirects with an error message if the user does not have permission.

- **`add_jobsearch`**:
  - **Purpose**: Handle the addition of a new job search.
  - **Functionality**:
    - Requires superuser access.
    - Handles form submission for adding a job search.
    - Provides success and error messages based on form validation and job application count.
    - Renders `jobs/add_jobsearch.html` with the form.

- **`edit_jobsearch`**:
  - **Purpose**: Handle editing of an existing job search.
  - **Functionality**:
    - Loads the job search instance for the given ID.
    - Handles form submission for updating the job search.
    - Renders `jobs/edit_jobsearch.html` with the form and jobsearch details.

- **`delete_jobsearch`**:
  - **Purpose**: Handle the deletion of a job search.
  - **Functionality**:
    - Deletes the job search instance for the given ID upon POST request.
    - Redirects with a success message if deletion is successful.
    - Redirects with an error message if the request method is invalid.

- **`job_search_view`**:
  - **Purpose**: Render the job search view with job search status indicators.
  - **Functionality**:
    - Retrieves and colors job searches based on their status.
    - Renders `jobs/job_search_view.html` with job search details.

- **`favs_display`**:
  - **Purpose**: Render the display of favorite jobs.
  - **Functionality**:
    - Requires user authentication.
    - Filters and displays favorite jobs.
    - Redirects with an error message if the user is not logged in.

# Views

- **`HomeView`**:
  - **Purpose**: Render the home page.
  - **Functionality**:
    - Handles GET requests.
    - Renders `home.html`.

- **`GeocodingView`**:
  - **Purpose**: Fetch and render geocoding data based on a place ID.
  - **Functionality**:
    - Handles GET requests with a `pk` parameter (place ID).
    - Requests geocoding data from the Google Maps API.
    - Renders `geocoding.html` with geocoding data or an error message if the request fails.

- **`DistanceView`**:
  - **Purpose**: Fetch and render distance matrix data based on origin and destination.
  - **Functionality**:
    - Handles GET requests with `origin` and `destination` parameters.
    - Requests distance data from the Google Maps API.
    - Renders `distance.html` with distance data or an error message if the request fails.

- **`MapView`**:
  - **Purpose**: Render a page with a map.
  - **Functionality**:
    - Handles GET requests.
    - Renders `map.html` with the Google API key for map functionality.

# OAuth2 and Environment Variables Views

- **`oauth2callback`**:
  - **Purpose**: Handle the OAuth2 callback from Google and exchange the authorization code for an access token.
  - **Functionality**:
    - Retrieves the authorization code from the request.
    - Exchanges the code for an access token by making a POST request to Google's token endpoint.
    - Stores the access token in the session.
    - Redirects to the dashboard or handles errors if the process fails.

- **`refresh_tokens`**:
  - **Purpose**: Refresh OAuth2 tokens if they are expired.
  - **Functionality**:
    - Checks if the credentials are expired and if a refresh token is available.
    - Refreshes the credentials and saves them to the database.
    - Logs the result or any errors encountered during the process.

- **`get_oauth2_authorization_url`**:
  - **Purpose**: Generate OAuth2 authorization URL.
  - **Functionality**:
    - Reads Google credentials from environment variables.
    - Constructs the OAuth2 authorization URL with the necessary parameters.
    - Logs and returns the authorization URL or raises an error if something goes wrong.

- **`oauth_login`**:
  - **Purpose**: Handle OAuth2 login by redirecting to the authorization URL.
  - **Functionality**:
    - Configures OAuth2 client using settings.
    - Generates the authorization URL and redirects the user to it.
    - Logs the authorization URL or any errors that occur during the process.

- **`env_vars`**:
  - **Purpose**: Return environment variables as a JSON response.
  - **Functionality**:
    - Retrieves and returns selected environment variables as JSON.
    - Useful for debugging and verifying configuration settings.


# Task Management Views

- **`task_list`**:
  - **Purpose**: Display a list of tasks and handle task creation via a form.
  - **Functionality**:
    - Retrieves all tasks and initializes a `TaskForm`.
    - Handles POST requests to create new tasks if the form is valid.
    - Renders the task list and form in `tasks/list.html`.

- **`create_task`**:
  - **Purpose**: Create a new task via a POST request and return a JSON response.
  - **Functionality**:
    - Extracts task details from the POST request.
    - Creates a new task and returns its details in a JSON response.
    - Handles invalid requests with an error message.

- **`update_task`**:
  - **Purpose**: Update an existing task based on its primary key (pk).
  - **Functionality**:
    - Retrieves the task by pk.
    - Handles POST requests to update the task using `TaskForm`.
    - Renders the update form or redirects to the task list upon success.

- **`delete_task`**:
  - **Purpose**: Delete a task based on its primary key (pk).
  - **Functionality**:
    - Retrieves the task by pk.
    - Deletes the task if the request method is POST.
    - Renders a confirmation page in `tasks/delete.html` for the deletion.

- **`toggle_task_complete`**:
  - **Purpose**: Toggle the completion status of a task.
  - **Functionality**:
    - Retrieves the task by its ID.
    - Toggles the `complete` status and saves the task.
    - Redirects to the task list.

