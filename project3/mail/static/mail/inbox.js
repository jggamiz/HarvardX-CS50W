document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Add event listener to the compose form
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


function send_email(event) {
  // Prevent default form submission
  event.preventDefault();

  // Get values from the form
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.message) {
      console.log(result.message);
      // Load the sent mailbox
      load_mailbox('sent');
    } else {
      console.error(result.error);
      alert(`Error: ${result.error}`);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}


function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
      .then(response => response.json())
      .then(emails => {
          // Print emails
          console.log(emails);
          render_emails(mailbox, emails);
      });
}


function render_emails(mailbox, emails) {
  // Clear any existing content
  const container = document.querySelector('#emails-view');
  container.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  emails.forEach(email => {
    const emailDiv = document.createElement('div');
    emailDiv.className = `email-box ${email.read ? 'read' : 'unread'}`;
    emailDiv.innerHTML = `
      <strong>${email.sender || "Unknown Sender"}</strong>
      <span>${email.subject}</span>
      <span class="timestamp">${email.timestamp}</span>
    `;

    emailDiv.addEventListener('click', () => load_email(email.id, mailbox));
    container.appendChild(emailDiv);
  });
}


function load_email(emailId, mailbox) {
  // Show the email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  // Fetch email details
  fetch(`/emails/${emailId}`)
    .then(response => response.json())
    .then(email => {
      // Print email
      const emailView = document.querySelector('#email-view');
      emailView.innerHTML = `
        <h3>${email.subject}</h3>
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <p><strong>Timestamp:</strong> ${email.timestamp}</p>
        <hr>
        <p>${email.body}</p>
        <hr>
        <button id="archive-button">${mailbox === 'inbox' ? 'Archive' : 'Unarchive'}</button>
        <button id="reply-button">Reply</button>
      `;

      // Archive/Unarchive button
      document.querySelector('#archive-button').addEventListener('click', () => {
        const isArchived = mailbox === 'inbox';
        fetch(`/emails/${emailId}`, {
          method: 'PUT',
          body: JSON.stringify({ archived: isArchived })
        })
        .then(response => {
          if (response.ok) {
            console.log(`Email successfully ${isArchived ? 'archived' : 'unarchived'}`);
            load_mailbox('inbox');
          } else {
            console.error('Failed to archive/unarchive the email.');
          }
        })
        .catch(error => console.error('Error archiving/unarchiving email:', error));
      });

      // Reply button
      document.querySelector('#reply-button').addEventListener('click', () => {
        load_compose_form(email);
      });

      // Mark the email as read
      if (!email.read) {
        fetch(`/emails/${emailId}`, {
          method: 'PUT',
          body: JSON.stringify({ read: true })
        });
      }
    });
}


function load_compose_form(originalEmail) {
  // Show the compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Get the compose form fields
  const recipientField = document.querySelector('#compose-recipients');
  const subjectField = document.querySelector('#compose-subject');
  const bodyField = document.querySelector('#compose-body');

  // Pre-fill the recipient with the original email sender
  recipientField.value = originalEmail.sender;

  if (originalEmail.subject.startsWith('Re: ')) {
    subjectField.value = originalEmail.subject;
  } else {
    subjectField.value = `Re: ${originalEmail.subject}`;
  }

  // Pre-fill the body with a reference to the original email's content
  bodyField.value = `On ${originalEmail.timestamp}, ${originalEmail.sender} wrote:\n\n${originalEmail.body}\n\n`;
}