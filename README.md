# test-task-paxful

## Deploy

for deploy application you can run file `deploy.sh` in directory `helm`

for postgresql used https://github.com/bitnami/charts/tree/master/bitnami/postgresql

Application parameters:
```yaml
postgresql:
  port: "5432" #Db port
  user: "app_test" # db user
  db: "app" #db_name
  password: "123qwe" #db password
email:
  send: "false" #set true for sending email when user blocked
  sender: "your-email@gmail.com" #sender email
  smtp_server: "smtp.gmail.com" #smtp server
  receiver: "test@domain.com" #who should receive email
  smtp_port: "465" # smtp port
  password: "your-password" #password for smtp server
app:
  port: "80" # service-port for application
  hostname: "test-app.localhost" #hostname for ingress
  image: "test-app:test" #application image
```
## Usage

Application has next endpoints:

`http://app/` - return Hello, if you send request
like `http://app/?n=x` where n is numeber you will get
answer `{"Result": n*n}`


`http://app/blacklisted` - add your ip to blacklist,
return error code 444 end send email,
if parameter send email was activated in helm values

`http://app/list_blacklist` - return list with blacklisted users

`http://app/unban/?ip=<banned_ip>` - remove user from ban list

## Tests

for testing you should run file `test.sh` from directory `tests`
